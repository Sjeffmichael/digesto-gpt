from django.contrib.messages import DEFAULT_LEVELS
from django_components import component


@component.register("toast_notifications")
class ToastNotifications(component.Component):
    template_name = "toast_notifications/template.html"

    def get_context_data(self, messages=None, websocket=False):
        if messages is None:
            messages = []
        return {
            "messages": messages,
            "websocket": websocket,
            "DEFAULT_MESSAGE_LEVELS": DEFAULT_LEVELS,
        }

    class Media:
        css = "toast_notifications/style.css"
        js = "toast_notifications/script.js"
