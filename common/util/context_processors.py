from urllib.parse import urlparse


def current_section(request):
    if hasattr(request, "scope"):
        request_url = request.scope.get("path")
    else:
        request_url = request.path

    return {"current_section": str(request_url).replace("/", "")}
