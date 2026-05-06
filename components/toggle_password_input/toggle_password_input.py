from django_components import component


@component.register("toggle_password_input")
class TogglePasswordInput(component.Component):
    template_name = "toggle_password_input/template.html"

    def get_context_data(self):
        return {}

    class Media:
        css = "toggle_password_input/style.css"
        js = "toggle_password_input/script.js"
