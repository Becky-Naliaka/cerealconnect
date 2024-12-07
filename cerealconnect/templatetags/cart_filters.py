# cerealconnect/templatetags/cart_filters.py
from django import template

register = template.Library()


# Example of a custom filter (you can add others as needed)
@register.filter
def currency(value):
    """Formats value as currency."""
    try:
        return f"KSh {value:,.2f}"
    except (ValueError, TypeError):
        return value
