from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def addition(value, arg):
    return Decimal(value) + Decimal(arg)

@register.filter
def subtraction(value, arg):
    return Decimal(value) + Decimal(arg)
