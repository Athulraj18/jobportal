# core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, delimiter=','):
    """Split a string by delimiter and strip whitespace around each part."""
    if not value:
        return []
    return [part.strip() for part in value.split(delimiter)]

@register.filter
def trim(value):
    """Trim leading/trailing whitespace."""
    return value.strip() if isinstance(value, str) else value
