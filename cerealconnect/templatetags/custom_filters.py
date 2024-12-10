# cerealconnect/templatetags/custom_filters.py
from django import template
from django.utils.formats import number_format

register = template.Library()


@register.filter
def multiply(value, arg):
    """Multiplies the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def currency(value):
    """Formats the value as currency."""
    try:
        return f"KSh {float(value):,.2f}"  # Formats with two decimal places
    except (ValueError, TypeError):
        return value  # Return original value if there's an error


@register.filter
def range_stars(value):
    """
    Returns a range from 1 to 5 for displaying star ratings.
    Ensures a valid range even if the value is None or invalid.
    """
    try:
        value = int(value) if value is not None else 0
        return range(1, 6)  # Always return a range from 1 to 5 stars
    except (TypeError, ValueError):
        return range(1, 6)


@register.filter
def currency_usd(value):
    """
    Formats the value as USD currency.
    """
    try:
        return f"${number_format(value, 2)}"
    except (ValueError, TypeError):
        return value  # Return the value as is if it's not a valid number


@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def to(value, end):
    try:
        return range(int(value), int(end))
    except ValueError:
        return []


@register.filter
def round(value):
    """
    Rounds a value to the nearest integer.
    """
    try:
        return int(round(float(value)))
    except (ValueError, TypeError):
        return value


@register.filter(name='add_class')
def add_class(field, css_class):
    """
    Adds a CSS class to form field widgets.
    """
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={"class": css_class})
    else:
        return mark_safe(str(field))
