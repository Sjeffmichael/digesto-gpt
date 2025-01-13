import logging

from django.core.management import call_command


def is_language_switcher_request(request):
    """
    Utility to validate if a request is sent from language switcher
    """
    return request.headers.get("Hx-Trigger") == "language-switcher"


def compile_locale_files():
    try:
        call_command("makemessages", "--all", "--ignore=env")
        call_command(
            "makemessages",
            "--all",
            "--ignore=env",
            "--extension=js",
            "--domain=djangojs",
            "--ignore=apps/theme",
        )
        call_command("compilemessages", "--ignore=env")
    except Exception as e:
        logging.error(e, stack_info=True)
