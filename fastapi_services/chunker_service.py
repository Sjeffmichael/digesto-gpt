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

from fastapi_services.RAG import RAG
from utils.custler_semantic_chunker import ClusterSemanticChunker
from tqdm import tqdm
from semantic_chunkers import StatisticalChunker
from semantic_router.encoders import HuggingFaceEncoder

load_dotenv(".env")


# Initialize Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")
django.setup()

from apps.digest_data.models import Law  # noqa: E402
from apps.chats.models import Message  # noqa: E402
from apps.digest_data.models import TextChunk  # noqa: E402

app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

DIGEST_FILES_DIR = apps.get_app_config("digest_data").path + "/files"
LAWS_DIR = DIGEST_FILES_DIR + "/laws"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MILVUS_URI = os.environ.get("MILVUS_DB_URI")
MODELS_CHACHE_DIR = os.environ.get("MODELS_CHACHE_DIR")
EMBEDDINGS_MODEL = os.environ.get("EMBEDDINGS_MODEL")
RERANKER_MODEL = os.environ.get("RERANKER_MODEL")


@sync_to_async
def get_law_by_id(id):
    return Law.objects.filter(id=id).first()


@sync_to_async
def get_all_laws_chunks():
    return list(TextChunk.objects.all().order_by("law", "fragment_number"))


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


chunker_encoder = HuggingFaceEncoder(
    name=EMBEDDINGS_MODEL,
    tokenizer_kwargs={"cache_dir": MODELS_CHACHE_DIR},
    model_kwargs={"cache_dir": MODELS_CHACHE_DIR},
    device="cuda",
    # device="cpu",
)


@app.post("/chunk-and-save-text")
async def chunk_and_save_text(request: Request):
    try:
        not_proccessed_laws = await get_not_proccessed_laws()
        for law in tqdm(not_proccessed_laws, "Laws"):
            # url = row #["reference"]
            # id = url.split("?idnorm=")[-1]
            # law = await get_law_by_id(id)
            # if id != "Mzkx#":
            #     continue

            with open(os.path.join(LAWS_DIR, law.filename)) as law_file:
                soup = BeautifulSoup(law_file.read(), "html.parser")
                chunker = StatisticalChunker(
                    chunker_encoder,
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
            try:
                await update_proccessed_law(law.id)
            except Exception as e:
                logging.error(e, stack_info=True, exc_info=True)

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


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
