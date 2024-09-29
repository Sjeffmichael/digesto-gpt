import asyncio
import json
import uuid
from random import randrange
from time import sleep
from urllib.parse import urlparse

# isort: off
from channels.generic.websocket import (
    AsyncWebsocketConsumer,
    WebsocketConsumer,
)
from django.template.loader import render_to_string
from django.utils.lorem_ipsum import words

from apps.user_authentication.models import User

from .models import Conversation, Message
from .services.response_generator import ResponseGenerator


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_generator = ResponseGenerator()

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        headers = text_data_json.get("HEADERS")
        message = text_data_json.get("message")
        current_url = headers.get("HX-Current-URL")
        parsed_url = urlparse(current_url)
        email = self.scope.get("user")
        id_ = ""
        conversation = None
        if not parsed_url.path.replace("/", ""):
            # create new conversation
            id_ = uuid.uuid4().hex
            user = User.objects.get(email=email)
            conversation_title = self.response_generator.generate_title(
                message,
            )

            conversation = Conversation.objects.create(
                slug=id_,
                user=user,
                title=conversation_title,
            )

            # send message to replace the current url
            self.send(json.dumps({"Hx-New-URL": current_url + id_}))
            # new chat item with title
            chat_title = render_to_string(
                "chats/conversations_list_item.html",
                {
                    "title": conversation_title,
                    "slug": id_,
                },
            )
            self.send(chat_title)
        else:
            conversation = Conversation.objects.get(
                slug=parsed_url.path.replace("/", "")
            )
            pass

        created_messages = Message.objects.create(
            conversation=conversation,
            user_message=message,
        )

        user_message_html = render_to_string(
            "chats/user_message.html",
            {
                "id": "msg_id_" + id_,
                "user_email": email,
                "message": {
                    "user_message": created_messages.user_message,
                },
            },
        )
        self.send(user_message_html)
        tokens = ""

        for token in self.response_generator.generate_response(message):
            tokens += token.content
            template_p = render_to_string(
                "chats/bot_message_token.html",
                {"id": "msg_id_" + id_, "token": token.content},
            )
            self.send(template_p)

        created_messages.bot_message = tokens
        created_messages.save()
