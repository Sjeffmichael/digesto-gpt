# isort: off
import json
import logging
import mimetypes
import os
import random
from dataclasses import dataclass
from typing import Any, List

import html2text
from asgiref.sync import sync_to_async
from bs4 import BeautifulSoup
from django.apps import apps
from dotenv import load_dotenv
from langchain.globals import set_debug
from langchain.prompts import ChatPromptTemplate
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_core.callbacks import FileCallbackHandler, StdOutCallbackHandler
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableParallel,
    RunnablePassthrough,
    RunnableSerializable,
)
from langchain_experimental.text_splitter import SemanticChunker
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface.embeddings import huggingface as hf
from langchain_milvus import BM25BuiltInFunction, Milvus
from langchain_milvus.retrievers import MilvusCollectionHybridSearchRetriever
from langchain_milvus.utils.sparse import BaseSparseEmbedding
from pymilvus import WeightedRanker
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import LLMContextRecall
from tqdm import tqdm

from apps.digest_data.models import Law

load_dotenv(".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

handler_1 = FileCallbackHandler("/home/michael/dev/on_premise_gpt/logs/rag.log")
handler_2 = StdOutCallbackHandler()

LAWS_DIR = apps.get_app_config("digest_data").path + "/files/laws"


class CustomSparseEmbedding(BaseSparseEmbedding):

    def embed_query(self, query: str) -> str:
        return query

    def embed_documents(self, texts: List[str]) -> List[str]:
        """Embed search docs."""
        return texts


@dataclass
class RAG:

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        # model="gemini-2.0-flash",
        api_key=GEMINI_API_KEY,
        verbose=True,
        # callbacks=[cot]
    )
    dense_embeddings = hf.HuggingFaceEmbeddings(
        model_name="intfloat/multilingual-e5-large-instruct",
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    dense_field = "dense"
    dense_metric_type = "COSINE"
    dense_index_type = "HNSW"

    sparse_field = "sparse"
    sparse_metric_type = "BM25"
    sparse_index_type = "SPARSE_INVERTED_INDEX"

    text_field = "text"

    dense_index_param = {
        "metric_type": dense_metric_type,
        "index_type": dense_index_type,
    }
    sparse_index_param = {
        "metric_type": sparse_metric_type,
        "index_type": sparse_index_type,
    }

    # vector_db = Milvus(
    #     dense_embeddings,
    #     auto_id=True,
    # )

    vector_db = Milvus(
        dense_embeddings,
        builtin_function=BM25BuiltInFunction(
            input_field_names=text_field, output_field_names=sparse_field
        ),
        index_params=[dense_index_param, sparse_index_param],
        vector_field=[dense_field, sparse_field],
        consistency_level="Strong",
        auto_id=True,
    )
    semantic_text_splitter = SemanticChunker(dense_embeddings)
    recursive_text_splitters = RecursiveCharacterTextSplitter(
        chunk_size=400, separators=["\n\n", "\n", ".", "?", "!", " ", ""]
    )

    def format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def get_runnable(self) -> RunnableSerializable[Any, Any]:
        # set_verbose(True)
        set_debug(True)
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

        4. Extensión: Mantén las respuestas concisas y completas, entre 50 y 150 palabras.

        5. Formato: Utiliza, si es necesario, subtítulos o listas para organizar la información.

        Entrada:
        Pregunta: {question}
        Contexto: {context}
        Respuesta:
        """  # noqa: E501

        dense_search_params = {"metric_type": self.dense_metric_type, "params": {}}
        sparse_search_params = {"metric_type": self.sparse_metric_type}
        retriever = MilvusCollectionHybridSearchRetriever(
            collection=self.vector_db.col,
            rerank=WeightedRanker(0.5, 0.5),
            field_embeddings=[self.dense_embeddings, CustomSparseEmbedding()],
            anns_fields=[self.dense_field, self.sparse_field],
            field_search_params=[dense_search_params, sparse_search_params],
            top_k=100,
            text_field=self.text_field,
        )

        model = HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base")
        compressor = CrossEncoderReranker(model=model, top_n=10)
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, base_retriever=retriever
        )

        promp = ChatPromptTemplate.from_template(template)
        rag_chain_from_docs = (
            RunnablePassthrough.assign(
                context=(lambda x: self.format_docs(x["context"]))
            )
            | promp
            | self.llm
            | StrOutputParser()
        )

        rag_chain_with_source = RunnableParallel(
            {"context": compression_retriever, "question": RunnablePassthrough()}
        ).assign(
            answer=rag_chain_from_docs,
            context=lambda x: list(map(dict, x["context"])),
            references_url=lambda x: list(map(self.get_references_url, x["context"])),
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

    def asamble_retriever(self):
        pass

    def test_accuracy(self):
        # read sample data
        dataset = []
        evaluator_llm = LangchainLLMWrapper(self.llm)
        with open("fastapi_services/questions_dataset.json") as file:
            sample_data = json.loads(file.read())
            random.shuffle(sample_data)
            for index, data in enumerate(tqdm(sample_data, desc="Evaluating")):
                question = data.get("question")
                reference = data.get("answer")
                if question and reference:
                    result = self.generate_response(question)
                    dataset.append(
                        {
                            "user_input": question,
                            "retrieved_contexts": list(
                                map(lambda x: x["page_content"], result.get("context"))
                            ),
                            "response": result.get("answer"),
                            "reference": reference,
                        }
                    )
                    # if index == 2:
                    #     break
            print("_" * 5 + "Dataset" + "_" * 5)
            print(dataset)
            evaluation_dataset = EvaluationDataset.from_list(dataset)
            evaluation_result = evaluate(
                dataset=evaluation_dataset,
                metrics=[LLMContextRecall()],
                llm=evaluator_llm,
            )

            evaluation_result.to_pandas().to_html("evaluation_result.html")

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

    def custom_text_splitter(self, html_text):
        # split by article
        soup = BeautifulSoup(html_text, "html.parser")
        articles = soup.find_all("div", class_="hcontainer article", recursive=True)
        split_result = []

        # container title
        # container preamble
        # container body
        # container conclusions
        #

        for article in tqdm(articles, "Processing articles:"):
            current_parent = article.find_parent()
            collected_elements = []
            while current_parent:
                # Find all matching elements inside the current parent
                found_elements = current_parent.find_all(
                    "span",
                    class_=[
                        "inline docType",
                        "inline docNumber",
                        "inline docTitle",
                        "inline heading",
                        "inline num",
                    ],
                    recursive=False,
                )
                collected_elements.extend(found_elements)

                current_parent = current_parent.find_parent()

            article_data = list(map(lambda x: x.text, collected_elements))

            split_result.append("\n".join(article_data + [article.text]))

        return split_result
