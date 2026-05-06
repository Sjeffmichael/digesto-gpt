import ast
import json

import markdown
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
@stringfilter
def render_markdown(value):
    md = markdown.Markdown(extensions=["fenced_code"])
    return mark_safe(md.convert(value))  # nosec B308 B703


@register.filter
def str_to_list(value):
    return ast.literal_eval(value) if value is not None else []
