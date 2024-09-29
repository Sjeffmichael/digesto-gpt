import os

from dotenv import load_dotenv
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ResponseGenerator:
    def __init__(self) -> None:
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.0-pro",
            api_key=GEMINI_API_KEY,
            verbose=True,
            # callbacks=[],
            temperature=0.9,
        )

    def generate_response(self, input_message: str):
        return self.llm.stream(input_message)

    def generate_title(self, input_message: str):
        template = """
        Genera un título corto para un chat basandote en el siguiente mensaje.
        Mensaje: {message}
        """
        prompt = ChatPromptTemplate.from_template(template)
        llm_chain = prompt | self.llm | StrOutputParser()
        return llm_chain.invoke(
            {
                "message": input_message,
            }
        )
