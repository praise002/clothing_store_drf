from django import template

register = template.Library()

@register.filter(is_safe=False)
def length_is(value, arg):
    
    try:
        return len(value) == int(arg)
    except (ValueError, TypeError):
        return ""

# https://stackoverflow.com/questions/78874958/invalid-filter-length-is-error-in-django-template-how-to-fix