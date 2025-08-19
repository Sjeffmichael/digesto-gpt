import json
import logging
import time
import uuid
from urllib.parse import urlparse

# isort: off
from channels.generic.websocket import (
    WebsocketConsumer,
)
from django.template.loader import render_to_string
from django.utils.lorem_ipsum import words
from django.contrib.messages import DEFAULT_LEVELS
from django.middleware.csrf import get_token

from apps.user_authentication.models import User

from .models import Conversation, Message
from .services.response_generator import ResponseGenerator
from components.toast_notifications.toast_notifications import (
    ToastNotifications,
)


class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response_generator = ResponseGenerator()
        print("ChatConsumer initialized ", args, kwargs)
        # self.csrf_token = get_token(self.scope["session"])

    def connect(self):
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        try:

            text_data_json = json.loads(text_data)
            headers = text_data_json.get("HEADERS")
            message = text_data_json.get("message")
            current_url = headers.get("HX-Current-URL")
            parsed_url = urlparse(current_url)
            email = self.scope.get("user")
            id_ = ""
            # csfr_token = get_token(self.scope)
            conversation = None
            if not parsed_url.path.replace("/", ""):
                # create new conversation
                id_ = uuid.uuid4().hex
                user = User.objects.get(email=email)
                # conversation_title = "Test Title"
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
                        # "slug": id_,
                        "created_date": conversation.created_date,
                        "csrf_token": self.scope["cookies"]["csrftoken"],
                    },
                )
                self.send(chat_title)
            else:
                conversation = Conversation.objects.get(
                    slug=parsed_url.path.replace("/", "")
                )

            created_messages = Message.objects.create(
                conversation=conversation,
                user_message=message,
            )

            user_message_html = render_to_string(
                "chats/user_message.html",
                {
                    "id": id_,
                    "user_email": email,
                    "message": {
                        "user_message": created_messages.user_message,
                        "id": created_messages.id,
                    },
                },
            )
            self.send(user_message_html)
            tokens = ""

            start_time = time.time()
            for chunk in self.response_generator.generate_response(
                message, created_messages.id
            ):
                try:

                    token = json.loads(chunk)
                    if token.get("answer"):
                        tokens += token.get("answer")
                        template_p = render_to_string(
                            "chats/bot_message_token.html",
                            {"id": created_messages.id, "token": tokens},
                        )
                        self.send(template_p)
                except json.JSONDecodeError as e:
                    logging.error(f"Corrupted JSON chunk received: {chunk}")
                    logging.error(
                        f"JSON decode error: {e}", exc_info=True, stack_info=True
                    )
                    continue

            print("Generate response duration: ", time.time() - start_time)

            created_messages.bot_message = tokens
            created_messages.save()
        except Exception as e:
            logging.error(f"Error in ChatConsumer: {e}", exc_info=True, stack_info=True)
            self.send(
                ToastNotifications.render(
                    kwargs={
                        "messages": [
                            {
                                "text": "Algo salió mal, intentelo más tarde.",
                                "level": DEFAULT_LEVELS["ERROR"],
                            }
                        ],
                        "websocket": True,
                    },
                )
            )
