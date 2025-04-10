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

from fastapi_services.RAG import RAG
from utils.custler_semantic_chunker import ClusterSemanticChunker

load_dotenv(".env")

# Initialize Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")
django.setup()

from apps.digest_data.models import Law  # noqa: E402
from apps.chats.models import Message  # noqa: E402


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


LAWS_DIR = apps.get_app_config("digest_data").path + "/files/laws"


@sync_to_async
def get_all_laws():
    return list(Law.objects.all())


@app.post("/chunk-and-save")
async def chunk_and_save_text(request: Request):

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


@app.post("/chunk-and-save-custom-splitter")
async def chunk_and_save_text_custom_splitter(request: Request):
    try:
        list_of_laws = [
            "Norma_902.html",
            "Norma_963.html",
            "Norma_s_n(3).html",
            "Norma_870.html",
            "Norma_1035.html",
            "Norma_641.html",
            "Norma_1058.html",
        ]

        for law in list_of_laws:
            with open(os.path.join(LAWS_DIR, law)) as law_file:
                chunks = rag_service.custom_text_splitter(law_file.read())

                await rag_service.vector_db.aadd_texts(chunks)
    except Exception as e:
        logging.error(e, stack_info=True, exc_info=True)


@app.post("/evaluate-rag")
async def evaluate_rag(request: Request):
    rag_service.test_accuracy()

    return ""


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
