from real_estate_agency.models import RealEstateAgency
from django.core.exceptions import ObjectDoesNotExist
from django import template

register = template.Library()

@register.simple_tag
def get_real_estate_agency(user):
    if user.is_anonymous:
        return None

    try:
        return RealEstateAgency.objects.get(
            representative=user,
        )
    except ObjectDoesNotExist:
        return None
