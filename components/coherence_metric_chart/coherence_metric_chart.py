from django_components import component


@component.register("coherence_metric_chart")
class CoherenceMetricChart(component.Component):
    template_name = "coherence_metric_chart/template.html"

    def get_context_data(self):
        return {}

    class Media:
        css = "coherence_metric_chart/style.css"
        js = "coherence_metric_chart/script.js"
