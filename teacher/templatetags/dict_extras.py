# app/templatetags/dict_extras.py
from django import template
register = template.Library()

@register.filter
def lookup(d, key):
    return d.get(key, "")


