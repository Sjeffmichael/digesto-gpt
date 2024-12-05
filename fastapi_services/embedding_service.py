import json
import os
import sys
import threading
from typing import List

# isort: off
import django
import uvicorn
from datasets import Dataset
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Request
from fastapi.responses import StreamingResponse
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_community.vectorstores import milvus
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from langchain_huggingface.embeddings import huggingface as hf
from pydantic import BaseModel
from ragas import evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.integrations.langchain import EvaluatorChain
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
    context_utilization,
    faithfulness,
)
from ragas.metrics.base import EvaluationMode
from ragas.metrics.critique import (
    coherence,
    conciseness,
    correctness,
    harmfulness,
    maliciousness,
)

load_dotenv(".env")
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "on_premise_gpt.settings")
# Initialize Django
django.setup()

from apps.chats.models import Message  # noqa: E402

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

app = FastAPI()

llm = ChatGoogleGenerativeAI(
    model="gemini-1.0-pro",
    api_key=GEMINI_API_KEY,
    verbose=True,
    # callbacks=[],
    # temperature=0.9,
)

embedding_model = hf.HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large-instruct",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

langchain_llm = LangchainLLMWrapper(
    GoogleGenerativeAI(
        model="gemini-1.0-pro",
        google_api_key=GEMINI_API_KEY,
        verbose=True,
    )
)

langchain_embeddings = LangchainEmbeddingsWrapper(embedding_model)

vector_db = milvus.Milvus(
    embedding_model, connection_args={"host": "127.0.0.1", "port": "19530"}
)


retriever = vector_db.as_retriever()

faithfulness_metric = Faithfulness()
answer_relevancy_metric = AnswerRelevancy(evaluation_mode=EvaluationMode.qac)
context_recall_metric = ContextRecall(evaluation_mode=EvaluationMode.qac)
context_precision_metric = ContextPrecision(evaluation_mode=EvaluationMode.qac)


class Documents(BaseModel):
    documents: List[str]


@app.post("/generate-title")
async def generate_title(request: Request):
    body = await request.json()
    input_message = body.get("input_message")
    template = """
    Genera un título corto para un chat basandote en el siguiente mensaje.
    Mensaje: {message}
    """
    prompt = ChatPromptTemplate.from_template(template)
    llm_chain = prompt | llm | StrOutputParser()
    result = await llm_chain.ainvoke(
        {
            "message": input_message,
        }
    )

    return result


def ragas_metrics(metrics_data, message_id):
    dataset = Dataset.from_dict(metrics_data)
    score = evaluate(
        dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_utilization,
            # harmfulness, maliciousness,
            coherence,
            correctness,
            conciseness,
        ],
        llm=langchain_llm,
        embeddings=langchain_embeddings,
    )
    message = Message.objects.get(id=message_id)
    message.metrics = score
    message.save()

    print(score)


# @shared_task
# def answer_metrics():
#     print("entro")


async def dump_results(results, message_id):
    metrics_data = {}
    answer = ""

    async for result in results:
        if result.get("question"):
            metrics_data["question"] = [result.get("question")]
        elif result.get("answer"):
            answer += result.get("answer")
        elif result.get("context"):
            metrics_data["contexts"] = [
                list(map(lambda x: x["page_content"], result.get("context")))
            ]
        # yield json.dumps({})
        yield json.dumps(result)

    metrics_data["answer"] = [answer]

    x = threading.Thread(
        target=ragas_metrics,
        kwargs={"metrics_data": metrics_data, "message_id": message_id},
    )
    x.start()
    # answer_metrics.delay()

    # dataset = Dataset.from_dict(metrics_data)
    # score = evaluate(dataset, metrics=[
    #         faithfulness,
    #         answer_relevancy,
    #         context_utilization,
    #         # harmfulness, maliciousness,
    #         coherence, correctness, conciseness
    #     ],
    #     llm=langchain_llm,
    #     embeddings=langchain_embeddings
    # )


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_references_url(context: str):
    dict_context = dict(context)
    return dict_context.get("metadata").get("url")


@app.get("/generate-response", response_class=StreamingResponse)
async def generate_response(request: Request):
    template = """
    Eres un chatot para responder consultas sobre información contenida
    en el digesto jurídico Nicaraguese. Utiliza el proporcionado contexto para
    dar una respuesta detallada y bien explicada sobre la siguiente pregunta.
    Si no sabes la respuesta, simplemente di que no la sabes.

    Pregunta: {question}
    Contexto: {context}
    Respuesta: """
    body = await request.json()
    input_message = body.get("input_message")
    message_id = body.get("message_id")

    promp = ChatPromptTemplate.from_template(template)
    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | promp
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(
        answer=rag_chain_from_docs,
        context=lambda x: list(map(dict, x["context"])),
        references_url=lambda x: list(map(get_references_url, x["context"])),
    )

    result = rag_chain_with_source.astream(
        input_message,
    )

    return StreamingResponse(
        dump_results(result, message_id),
        # result,
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8080)
