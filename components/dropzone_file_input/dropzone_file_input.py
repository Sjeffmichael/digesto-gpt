from django_components import component


@component.register("dropzone_file_input")
class DropzoneFileInput(component.Component):
    template_name = "dropzone_file_input/template.html"

    def get_context_data(self):
        return {
            # "param": "sample value",
        }

    class Media:
        css = "dropzone_file_input/style.css"
        js = "dropzone_file_input/script.js"
