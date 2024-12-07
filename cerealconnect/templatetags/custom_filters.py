# cerealconnect/templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def mul(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def currency(value):
    """Format the value as currency."""
    try:
        return f"KSh {value:,.2f}"
    except (ValueError, TypeError):
        return value


@register.filter
def currency_filter(value):
    """Formats the number with the currency symbol."""
    try:
        return f"KSh {float(value):,.2f}"  # Formats with two decimal places
    except (ValueError, TypeError):
        return value  # Return original value if there's an error
