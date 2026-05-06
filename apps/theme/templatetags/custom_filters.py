import json
import uuid

from django import template

register = template.Library()


@register.filter
def generate_uuid(value):
    return str(uuid.uuid4())


@register.filter
def pretty_json(value):
    result = json.dumps(value, indent=4)
    print(result)
    return result
