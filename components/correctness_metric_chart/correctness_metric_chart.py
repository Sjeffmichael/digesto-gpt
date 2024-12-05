from django_components import component


@component.register("correctness_metric_chart")
class CorrectnessMetricChart(component.Component):
    template_name = "correctness_metric_chart/template.html"

    def get_context_data(self):
        return {}

    class Media:
        css = "correctness_metric_chart/style.css"
        js = "correctness_metric_chart/script.js"
