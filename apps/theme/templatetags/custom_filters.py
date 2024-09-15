import uuid

from django import template

register = template.Library()


@register.filter
def generate_uuid(value):
    return str(uuid.uuid4())
