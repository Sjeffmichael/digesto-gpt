from urllib.parse import urlparse


def current_section(request):
    request_url = request.scope.get("path")

    return {"current_section": str(request_url).replace("/", "")}
