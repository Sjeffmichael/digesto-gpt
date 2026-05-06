from django_components import component

from apps.digest_data.pydantic_models import LawDataFormContext


@component.register("law_data_form")
class LawDataForm(component.Component):
    template_name = "law_data_form/template.html"

    # def get_context_data(self, context_data):
    #     return context_data

    def get(self, request):
        pass

    class Media:
        css = "law_data_form/style.css"
        js = "law_data_form/script.js"
