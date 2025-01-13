from django_components import component


@component.register("generation_metrics_chart")
class GenerationMetricsChart(component.Component):
    template_name = "generation_metrics_chart/template.html"

    def get_context_data(self, total_answers):
        print(total_answers)
        return {
            "total_answers": total_answers,
        }

    class Media:
        css = "generation_metrics_chart/style.css"
        js = "generation_metrics_chart/script.js"
