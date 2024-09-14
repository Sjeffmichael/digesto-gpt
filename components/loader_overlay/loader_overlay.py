from django_components import component


@component.register("loader_overlay")
class LoaderOverlay(component.Component):
    template_name = "loader_overlay/template.html"

    def get_context_data(self):
        return {}

    class Media:
        css = "loader_overlay/style.css"
