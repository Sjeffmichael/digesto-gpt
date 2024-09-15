from django.contrib.messages import get_messages
from django.template.loader import render_to_string

from components.toast_notifications.toast_notifications import (
    ToastNotifications,
)


class HtmxMessagesMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        messages = get_messages(request)

        if messages:
            response.write(
                ToastNotifications.render(
                    kwargs={"messages": messages},
                )
            )

        return response
