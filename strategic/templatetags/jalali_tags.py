import datetime
from django import template
from strategic.jalali_utils import gregorian_to_jalali_str, jalali_today_str

register = template.Library()


@register.filter
def jalali(value):
    """Renders a Gregorian date/datetime as a Jalali date string. Use in templates: {{ some_date|jalali }}"""
    if not value:
        return "—"
    if isinstance(value, datetime.datetime):
        value = value.date()
    if not isinstance(value, datetime.date):
        return value
    return gregorian_to_jalali_str(value)


@register.simple_tag
def jalali_now():
    """Returns today's date as a Jalali string, e.g. ۱۴۰۵/۰۴/۱۲"""
    return jalali_today_str()


PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


@register.filter
def fanum(value):
    """Converts any digits in a number/string to Persian numerals. Use: {{ value|fanum }}"""
    if value is None:
        return ""
    return "".join(PERSIAN_DIGITS[int(ch)] if ch.isdigit() else ch for ch in str(value))
