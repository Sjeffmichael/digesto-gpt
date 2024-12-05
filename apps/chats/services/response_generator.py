import json

import httpx
import requests


class ResponseGenerator:

    def generate_response(self, input_message: str, message_id: int):
        with httpx.stream(
            "GET",
            "http://localhost:8080/generate-response",
            data=json.dumps({"input_message": input_message, "message_id": message_id}),
        ) as r:
            for chunk in r.iter_raw():
                yield chunk.decode()

    def generate_title(self, input_message: str):
        result = requests.post(
            "http://localhost:8080/generate-title",
            data=json.dumps({"input_message": input_message}),
            timeout=5,
        )
        return result.json()
