from django import template

# register is an object that helps us register new tags
register = template.Library()

@register.filter('select_field')
def select_field(camper_pk, select_fields):
    return select_fields[str(camper_pk)]