# isort: off
import json
import logging
import mimetypes
import os
from typing import Any, List
import sys

import django
import html2text
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.apps import apps
from dotenv import load_dotenv
from langchain.globals import set_debug, set_verbose
from langchain.prompts import ChatPromptTemplate

# from langchain.retrievers import ContextualCompressionRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableSerializable,
    RunnableLambda,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface.embeddings import huggingface as hf
from langchain_milvus import BM25BuiltInFunction, Milvus
from langchain_milvus.retrievers import MilvusCollectionHybridSearchRetriever
from langchain_milvus.utils.sparse import BaseSparseEmbedding
from pymilvus import RRFRanker
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    LLMContextRecall,
    LLMContextPrecisionWithReference,
    Faithfulness,
    ResponseRelevancy,
)
from tqdm import tqdm
from semantic_chunkers import StatisticalChunker
from semantic_router.encoders import HuggingFaceEncoder

load_dotenv(".env", verbose=True, override=True)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MILVUS_URI = os.environ.get("MILVUS_DB_URI")
MILVUS_TOKEN = os.environ.get("MILVUS_DB_TOKEN")
MODELS_CHACHE_DIR = os.environ.get("MODELS_CHACHE_DIR")
EMBEDDINGS_MODEL = os.environ.get("EMBEDDINGS_MODEL")

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")
django.setup()

from apps.digest_data.models import Law  # noqa: E402


LAWS_DIR = apps.get_app_config("digest_data").path + "/files/laws"


class CustomSparseEmbedding(BaseSparseEmbedding):

    def embed_query(self, query: str) -> str:
        return query

    def embed_documents(self, texts: List[str]) -> List[str]:
        """Embed search docs."""
        return texts


class RAG:

    def __init__(self):

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            api_key=GEMINI_API_KEY,
            verbose=True,
        )

        # load dense embeddings model for RAG
        self.dense_embeddings = hf.HuggingFaceEmbeddings(
            model_name=EMBEDDINGS_MODEL,
            # model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
            show_progress=True,
            cache_folder=MODELS_CHACHE_DIR,
        )

        self.dense_field = "dense"
        self.dense_metric_type = "COSINE"
        self.dense_index_type = "HNSW"

        self.sparse_field = "sparse"
        self.sparse_metric_type = "BM25"
        self.sparse_index_type = "SPARSE_INVERTED_INDEX"

        self.text_field = "text"

        self.dense_index_param = {
            "metric_type": self.dense_metric_type,
            "index_type": self.dense_index_type,
        }
        self.sparse_index_param = {
            "metric_type": self.sparse_metric_type,
            "index_type": self.sparse_index_type,
        }

        self.vector_db = Milvus(
            self.dense_embeddings,
            builtin_function=BM25BuiltInFunction(
                input_field_names=self.text_field, output_field_names=self.sparse_field
            ),
            index_params=[self.dense_index_param, self.sparse_index_param],
            vector_field=[self.dense_field, self.sparse_field],
            consistency_level="Strong",
            auto_id=True,
            connection_args={"uri": MILVUS_URI, "token": MILVUS_TOKEN},
        )

        self.dense_search_params = {"metric_type": self.dense_metric_type, "params": {}}
        self.sparse_search_params = {"metric_type": self.sparse_metric_type}

        self.hybrid_retriever = None

        self._initialize_retrievers()

    def _initialize_retrievers(self):
        print(self.vector_db.col)
        if self.vector_db.col and self.hybrid_retriever is None:
            self.hybrid_retriever = MilvusCollectionHybridSearchRetriever(
                collection=self.vector_db.col,
                rerank=RRFRanker(),
                field_embeddings=[self.dense_embeddings, CustomSparseEmbedding()],
                anns_fields=[self.dense_field, self.sparse_field],
                field_search_params=[
                    self.dense_search_params,
                    self.sparse_search_params,
                ],
                top_k=10,
                text_field=self.text_field,
            )

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_detailed_instruct(self, query: str) -> str:
        return f"Instruct: Dada la siguiente consulta legal, extrae los fragmentos relevantes para responder la consulta\nQuery: {query}"  # noqa: E501

    def get_runnable(self) -> RunnableSerializable[Any, Any]:
        # set_verbose(True)
        # set_debug(True)
        template = """
        Eres un abogado experto en análisis del Digesto Jurídico Nicaragüense. Tu objetivo es proporcionar respuestas precisas y completas a las consultas legales sobre Nicaragua, utilizando el Digesto Jurídico como única fuente de información.
        El contexto contiene extractos relevantes del Digesto Jurídico Nicaragüense.

        Instrucciones:

        1. Revisión del contexto: Antes de responder, revisa cuidadosamente el contexto para identificar la información más relevante.

        2. Estructuración de la respuesta: Organiza tu respuesta en tres secciones, pero no necesarimente pongas de forma explicitas esta estructura haz que sea como una redaccion fluida:

            - Resumen del extracto relevante (indicando la sección o artículo si es aplicable).

            - Análisis y parafraseo de los conceptos clave.

            - Conclusión o recomendación basada en la información disponible.

        3. Precisión y fidelidad:

            - Si la respuesta está directamente en el contexto, parafrasea y explica los conceptos sin alterar el significado.

            - Si no se encuentra explícitamente, infiere una respuesta lógica. Si la inferencia no es posible o hay ambigüedad, indica que no es posible responder con certeza y explica brevemente por qué.

            - Nunca inventes información que no esté en el contexto.

            - No brindes las referencias si no utilizas información del contexto proporcionado.

        4. Extensión: Mantén las respuestas concisas y completas, entre 50 y 150 palabras.

        5. Formato: Utiliza, si es necesario, subtítulos o listas para organizar la información.

        6. Genera la respuesta en el idioma en que se hace la pregunta, si se te pregunta en español responde en español, si te pregunta en ingles responde en ingles.

        7. Cuando utilices información de documentos, que esten derogados, sean derecho historico o sin vigencia, aclaralo en la respuesta.

        8. Por último agrega la o las URL de la información utilizada para responder a la pregunta como referencias, utilizando el siguiente formato:
        <h2 class="mt-2 text-sm font-semibold text-gray-900 dark:text-white">Referencias:</h2>
        <ul class="max-w-md space-y-1 text-gray-500 list-disc list-inside dark:text-gray-400">
            <li>
                <a href="http://referencia-1" target="_blank" class="font-medium text-blue-600 dark:text-blue-500 hover:underline break-all">http://referencia-1</a>
            </li>
            <li>
                <a href="http://referencia-2" target="_blank" class="font-medium text-blue-600 dark:text-blue-500 hover:underline break-all">http://referencia-2</a>
            </li>
        </ul>

        Entrada:
        Pregunta: {question}
        Contexto: {context}
        Respuesta:
        """  # noqa: E501

        self._initialize_retrievers()

        promp = ChatPromptTemplate.from_template(template)
        rag_chain_from_docs = (
            RunnablePassthrough.assign(
                context=(lambda x: self.format_docs(x["context"]))
            )
            | promp
            | self.llm
            | StrOutputParser()
        )

        context_runnable = RunnableLambda(lambda x: self.get_detailed_instruct(x)) | (
            self.hybrid_retriever
            if self.hybrid_retriever is not None
            else RunnableLambda(lambda x: [])
        )

        rag_chain_with_source = RunnableParallel(
            {"context": context_runnable, "question": RunnablePassthrough()}
        ).assign(
            answer=rag_chain_from_docs,
            context=lambda x: list(map(dict, x.get("context"))),
        )

        return rag_chain_with_source

    def generate_response(self, text: str, stream_response: bool = False):
        rag_runnable = self.get_runnable()
        if stream_response:
            return rag_runnable.astream(
                text,
            )

        return rag_runnable.invoke(
            text,
        )

    async def dump_results(self, results, message_id):
        metrics_data = {}
        answer = ""

        async for result in results:
            if result.get("question"):
                metrics_data["user_input"] = [result.get("question")]
            elif result.get("answer"):
                answer += result.get("answer")
            elif result.get("context"):
                metrics_data["retrieved_contexts"] = [
                    list(map(lambda x: x["page_content"], result.get("context")))
                ]

            yield json.dumps(result)

        metrics_data["response"] = [answer]

        # x = threading.Thread(
        #     target=ragas_metrics,
        #     kwargs={"metrics_data": metrics_data, "message_id": message_id},
        # )
        # x.start()

    def get_references_url(self, context: str):
        dict_context = dict(context)
        return dict_context.get("metadata").get("norma_url")

    def generate_dataset(self):
        pass

    def test_accuracy(self, dataset):

        evaluator_llm = LangchainLLMWrapper(self.llm)

        evaluation_dataset = EvaluationDataset.from_list(dataset)
        evaluation_result = evaluate(
            dataset=evaluation_dataset,
            metrics=[
                LLMContextRecall(),
                LLMContextPrecisionWithReference(),
                Faithfulness(),
                ResponseRelevancy(),
            ],
            llm=evaluator_llm,
            embeddings=self.dense_embeddings,
        )

        evaluation_result.to_pandas().to_csv("evaluation_result.csv", index=False)

    @sync_to_async
    def get_all_laws(self):
        return list(Law.objects.all())

    async def load_data(self):

        laws = await self.get_all_laws()
        for index, law in enumerate(tqdm(laws, "Reading Laws")):
            print(index)
            print(law.id)
            print(law.filename)
            extension = mimetypes.guess_extension(mimetypes.guess_type(law.filename)[0])
            try:
                with open(os.path.join(LAWS_DIR, law.id + extension)) as law_file:
                    text = html2text.html2text(law_file.read())

                    law.metadata.pop("norma_archivos_relacionados")

                    chunks = self.recursive_text_splitters.create_documents(
                        [text], [law.metadata]
                    )

                    Milvus.from_documents(
                        chunks,
                        self.dense_embeddings,
                        connection_args={"host": "127.0.0.1", "port": "19530"},
                    )

            except Exception as e:
                logging.error(e, stack_info=True, exc_info=True)

            if index == 4:
                break
