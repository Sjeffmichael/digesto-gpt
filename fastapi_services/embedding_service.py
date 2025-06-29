import logging
import mimetypes
import os
import sys
from typing import List

import html2text

# isort: off
import django
import uvicorn
from datasets import Dataset
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from langchain.prompts import ChatPromptTemplate
from langchain_milvus import Milvus
from pymilvus import MilvusClient
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    answer_relevancy,
    faithfulness,
    LLMContextPrecisionWithoutReference,
)
from django.apps import apps
from ragas.metrics._aspect_critic import coherence, conciseness, correctness
from asgiref.sync import sync_to_async
from pandas import read_csv, DataFrame
from bs4 import BeautifulSoup
import ast
import matplotlib.pyplot as plt
import numpy as np
from contextlib import redirect_stdout

from fastapi_services.RAG import RAG
from utils.custler_semantic_chunker import ClusterSemanticChunker
from tqdm import tqdm
from semantic_chunkers import StatisticalChunker

load_dotenv(".env")

# Initialize Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")
django.setup()

from apps.digest_data.models import Law  # noqa: E402
from apps.chats.models import Message  # noqa: E402
from apps.digest_data.models import TextChunk  # noqa: E402


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

rag_service = RAG()

langchain_llm = LangchainLLMWrapper(
    rag_service.llm
    # GoogleGenerativeAI(
    #     model="gemini-1.0-pro",
    #     google_api_key=GEMINI_API_KEY,
    #     verbose=True,
    # )
)

langchain_embeddings = LangchainEmbeddingsWrapper(rag_service.dense_embeddings)


class Documents(BaseModel):
    documents: List[str]


@app.post("/generate-title")
async def generate_title(request: Request):
    body = await request.json()
    input_message = body.get("input_message")
    template = """
    Genera unicamente un título corto para un chat basandote en el siguiente mensaje.
    Mensaje: {message}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm_chain = prompt | rag_service.llm | StrOutputParser()
    result = await llm_chain.ainvoke(
        {
            "message": input_message,
        }
    )

    return result


def ragas_metrics(metrics_data, message_id):
    dataset = Dataset.from_dict(metrics_data)
    print(dataset)
    score = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            LLMContextPrecisionWithoutReference(),
            # harmfulness, maliciousness,
            correctness,
            coherence,
            conciseness,
        ],
        llm=langchain_llm,
        embeddings=langchain_embeddings,
    )
    message = Message.objects.get(id=message_id)
    message.metrics = score
    message.save()

    print(score)


@app.get("/generate-response", response_class=StreamingResponse)
async def generate_response(request: Request):

    body = await request.json()
    input_message = body.get("input_message")
    message_id = body.get("message_id")

    result = rag_service.generate_response(input_message, True)

    return StreamingResponse(
        rag_service.dump_results(result, message_id),
        # result,
        media_type="text/event-stream",
    )


class TextData(BaseModel):
    text: str
    metadata: dict


def delete_all_from_db():
    vector_db = MilvusClient(uri="http://localhost:19530")

    vector_db.drop_collection(collection_name="LangChainCollection")


DIGEST_FILES_DIR = apps.get_app_config("digest_data").path + "/files"
LAWS_DIR = DIGEST_FILES_DIR + "/laws"


@app.post("/chunk-and-save")
async def chunk_and_save(request: Request):

    text_splitter = ClusterSemanticChunker(
        embedding_function=rag_service.dense_embeddings.embed_documents
    )

    laws = await get_all_laws()
    for index, law in enumerate(laws):
        extension = mimetypes.guess_extension(mimetypes.guess_type(law.filename)[0])
        try:
            with open(os.path.join(LAWS_DIR, law.id + extension)) as law_file:
                text = html2text.html2text(law_file.read())

                law.metadata.pop("norma_archivos_relacionados")

                chunks = text_splitter.create_documents([text])
                # embbed metadata into text
                for index_2, _ in enumerate(chunks):
                    chunks[index_2].page_content = (
                        "Número de la norma: {norma_numero}\n"
                        "Título: {norma_titulo}\n"
                        "Materia: {norma_materia}\n"
                        "Estado: {norma_estado}\n"
                        "Categoría: {norma_categoria}\n"
                        "Rango: {norma_rango}\n"
                        "Fecha publicación: {norma_fecha_publicacion}\n"
                        "Fecha aprobación: {norma_fecha_aprobacion}\n"
                        "URL: {norma_url}\n"
                        "{page_content}"
                    ).format(
                        norma_numero=law.metadata.get("norma_numero"),
                        norma_titulo=law.metadata.get("norma_titulo"),
                        norma_materia=law.metadata.get("norma_materia"),
                        norma_estado=law.metadata.get("norma_estado"),
                        norma_categoria=law.metadata.get("norma_categoria"),
                        norma_rango=law.metadata.get("norma_rango"),
                        norma_fecha_publicacion=law.metadata.get(
                            "norma_fecha_publicacion"
                        ),
                        norma_fecha_aprobacion=law.metadata.get(
                            "norma_fecha_aprobacion"
                        ),
                        norma_url=law.metadata.get("norma_url"),
                        page_content=chunks[index_2].page_content,
                    )

                    if index_2 == 1:
                        print(chunks[index_2])

                Milvus.from_documents(
                    chunks,
                    rag_service.dense_embeddings,
                    connection_args={"host": "127.0.0.1", "port": "19530"},
                )

        except Exception as e:
            logging.error(e, stack_info=True, exc_info=True)

        if index == 4:
            break

    return JSONResponse(content={"status": 1})


@sync_to_async
def get_law_by_id(id):
    return Law.objects.filter(id=id).first()


@sync_to_async
def get_not_proccessed_laws_chunks():
    return list(
        TextChunk.objects.filter(proccessed=False).order_by("law", "fragment_number")
    )


@sync_to_async
def get_all_laws():
    return list(Law.objects.all())


@sync_to_async
def get_not_proccessed_laws():
    return list(Law.objects.filter(proccessed=False))


@sync_to_async
def save_chunks_batch(chunks: List[TextChunk]):
    TextChunk.objects.bulk_create(
        chunks,
        update_conflicts=True,
        update_fields=["content"],
        unique_fields=["fragment_number", "law"],
    )


@sync_to_async
def update_proccessed_law(id: str):
    Law.objects.filter(id=id).update(proccessed=True)


@sync_to_async
def update_proccessed_chunks(id: int):
    TextChunk.objects.filter(id=id).update(proccessed=True)


@app.post("/chunk-and-save-dataset")
async def chunk_and_save_dataset(request: Request):
    try:

        dataset = read_csv(os.path.join(DIGEST_FILES_DIR, "digest_queries_dataset.csv"))
        unique_reference = dataset["reference"].dropna().unique().tolist()
        for index, row in enumerate(unique_reference):
            url = row  # ["reference"]
            id = url.split("?idnorm=")[-1]
            law = await get_law_by_id(id)
            if id != "Mzkx#":
                continue

            with open(os.path.join(LAWS_DIR, id + ".html")) as law_file:
                soup = BeautifulSoup(law_file.read(), "html.parser")
                chunks = rag_service.statistical_chunker(docs=[soup.text])

                metadata_str = ""
                for key, value in law.metadata.items():
                    metadata_str += "{key}: {value}\n".format(
                        key=key.replace("_", " ").replace("norma ", "").capitalize(),
                        value=value,
                    )

                    # if key == "norma_archivos_relacionados":
                    #     continue
                    # if key == "norma_numero":
                    #     metadata[key] = value.split("-")[0]
                # embbed metadata into text
                text_chunks = []
                for index_2 in range(len(chunks[0])):
                    frament_number = index_2 + 1
                    metadata_str2 = metadata_str + "Fragmento: {}\n".format(
                        frament_number
                    )
                    text_chunks.append(
                        TextChunk(
                            fragment_number=frament_number,
                            content=metadata_str2 + " ".join(chunks[0][index_2].splits),
                            law=law,
                        )
                    )

                await save_chunks_batch(text_chunks)

                with open("logs/chunks.log", "w") as f:
                    with redirect_stdout(f):
                        # print("hola mundo")
                        rag_service.statistical_chunker.print(chunks[0])
                        # pass
                        # rag_service.statistical_chunker.print(chunks[0])

                # await rag_service.vector_db.aadd_texts(chunks)
                # if index == 0:
                #     break
    except Exception as e:
        logging.error(e, stack_info=True, exc_info=True)


@app.post("/chunk-and-save-text")
async def chunk_and_save_text(request: Request):
    try:

        not_proccessed_laws = await get_not_proccessed_laws()
        for law in tqdm(not_proccessed_laws, "Laws"):
            with open(os.path.join(LAWS_DIR, law.filename)) as law_file:
                soup = BeautifulSoup(law_file.read(), "html.parser")
                chunker = StatisticalChunker(
                    rag_service.chunker_encoder,
                    plot_chunks=False,
                    max_split_tokens=500,
                    enable_statistics=True,
                )

                chunks = chunker(docs=[soup.text])

                del chunker
                metadata_str = ""
                for key, value in law.metadata.items():
                    metadata_str += "{key}: {value}\n".format(
                        key=key.replace("_", " ").replace("norma ", "").capitalize(),
                        value=value,
                    )

                # embbed metadata into text
                text_chunks = []
                for index_2 in range(len(chunks[0])):
                    frament_number = index_2 + 1
                    metadata_str2 = metadata_str + "Fragmento: {}\n".format(
                        frament_number
                    )
                    text_chunks.append(
                        TextChunk(
                            fragment_number=frament_number,
                            content=metadata_str2 + " ".join(chunks[0][index_2].splits),
                            law=law,
                        )
                    )

            await save_chunks_batch(text_chunks)
            await update_proccessed_law(law.id)

            # with open("logs/chunks.log", "w") as f:
            #     with redirect_stdout(f):
            # print("hola mundo")
            # rag_service.statistical_chunker.print(chunks[0])
            # pass
            # rag_service.statistical_chunker.print(chunks[0])

            # await rag_service.vector_db.aadd_texts(chunks)
            # if index == 0:
            #     break
            # break
    except Exception as e:
        logging.error(e, stack_info=True, exc_info=True)


@app.post("/evaluate-rag")
async def evaluate_rag(request: Request):
    queries_dataset = read_csv("dataset_result.csv")
    queries_dataset["retrieved_contexts"] = queries_dataset["retrieved_contexts"].apply(
        ast.literal_eval
    )
    # print(queries_dataset.to_dict(orient="records")[0:1])
    rag_service.test_accuracy(queries_dataset.to_dict(orient="records"))
    # rag_service.test_accuracy()

    return ""


@app.post("/embbed-and-save-data")
async def embbed_and_save_data(request: Request):
    laws_chunks = await get_not_proccessed_laws_chunks()
    # i = 0

    for chunk in tqdm(laws_chunks, desc="Laws"):
        # i += 1
        # id, law_id, fragment_number = await get_chunk_data(chunk)
        # print(id, law_id, fragment_number)
        # if i == 10:
        #     break
        # print(law.fragment_number)
        await rag_service.vector_db.aadd_texts(
            [chunk.content],
            metadatas=[{"law_id": chunk.__dict__.get("law_id")}],
        )
        await update_proccessed_chunks(chunk.id)

    return ""


@app.post("/generate-dataset")
async def generate_dataset(request: Request):
    queries_dataset = read_csv(
        os.path.join(DIGEST_FILES_DIR, "digest_queries_dataset.csv")
    )
    test_df = DataFrame(
        columns=["user_input", "retrieved_contexts", "response", "reference"]
    )

    for _, row in queries_dataset.dropna().iterrows():
        result = rag_service.generate_response(row["query"])
        # add the result to the dataframe
        test_df.loc[len(test_df)] = [
            row["query"],
            list(map(lambda x: x["page_content"], result.get("context"))),
            result.get("answer"),
            row["answer"],
        ]

    test_df.to_csv("dataset_result.csv", index=False)


@sync_to_async
def get_chunk_data(chunk):
    return chunk.id, chunk.law.id, chunk.fragment_number


@app.post("/generate-charts")
def generate_charts(request: Request):
    evaluation_result_df = read_csv("evaluation_result.csv")

    chart_data = [
        {
            "metric": "faithfulness",
            "title": "Fidelidad",
            "xlabel": "Consultas",
            "ylabel": "Puntuación",
        },
        {
            "metric": "llm_context_precision_with_reference",
            "title": "Precisión del Contexto",
            "xlabel": "Consultas",
            "ylabel": "Puntuación",
        },
        {
            "metric": "answer_relevancy",
            "title": "Relevancia de la Respuesta",
            "xlabel": "Consultas",
            "ylabel": "Puntuación",
        },
        {
            "metric": "context_recall",
            "title": "Recuperación del Contexto",
            "xlabel": "Consultas",
            "ylabel": "Puntuación",
        },
    ]

    for data in chart_data:
        y = list(
            map(lambda x: x * 100, evaluation_result_df[data.get("metric")].to_list())
        )
        y_len = len(y)
        x = 0.5 + np.arange(y_len)

        plt.bar(x, y)
        plt.title(data.get("title"))
        plt.xlabel(data.get("xlabel"))
        plt.ylabel(data.get("ylabel"))

        plt.savefig(data.get("metric") + ".png")

        plt.close()

    return ""


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
