from django_components import component


@component.register("conciseness_metric_chart")
class ConcisenessMetricChart(component.Component):
    template_name = "conciseness_metric_chart/template.html"

    def get_context_data(self):
        return {}

    class Media:
        css = "conciseness_metric_chart/style.css"
        js = "conciseness_metric_chart/script.js"
