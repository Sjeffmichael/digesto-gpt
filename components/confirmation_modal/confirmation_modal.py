from django_components import component


@component.register("confirmation_modal")
class ConfirmationModal(component.Component):
    template_name = "confirmation_modal/template.html"

    def get_context_data(self, title, id_="confirmation-modal"):
        return {
            "title": title,
            "id": id_,
        }

    class Media:
        css = "confirmation_modal/style.css"
        js = "confirmation_modal/script.js"
