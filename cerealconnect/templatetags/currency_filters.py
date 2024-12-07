from django import template

register = template.Library()


@register.filter
def currency_filter(value):
    """Formats the number with the currency symbol."""
    try:
        return f"KSh {float(value):,.2f}"  # Formats with two decimal places
    except (ValueError, TypeError):
        return value  # Return original value if there's an error
