from django_components import component

from apps.digest_data.pydantic_models import UserDataFormContext


@component.register("user_data_form")
class UserDataForm(component.Component):
    template_name = "user_data_form/template.html"

    def get_context_data(self, data_context: UserDataFormContext):
        return data_context.model_dump()

    def get(self, request):
        pass

    class Media:
        css = "user_data_form/style.css"
        js = "user_data_form/script.js"
