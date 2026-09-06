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


@register.filter
def get_item(d, key):
    """Dynamic dict lookup for templates: {{ mydict|get_item:some_var }}"""
    if not d:
        return None
    return d.get(key)


from django.utils.html import escape, mark_safe


@register.filter
def tows_split(value):
    """جداکردن نمایشی عنوان راهبرد TOWS از شرح آن — بدون تغییر خودِ داده‌ی
    ذخیره‌شده. هرجا کلمه‌ی «شرح:» توی متن پیدا بشه، از همون‌جا یه خط جدید و
    استایل کمی متفاوت (رنگ کم‌رنگ‌تر) برای بخش شرح اعمال می‌شه.
    استفاده: {{ st.text|tows_split }} (خروجی از قبل escape شده، با |safe نیاز نیست دوباره escape بشه)."""
    if not value:
        return ""
    text = str(value)
    idx = text.find("شرح:")
    if idx == -1:
        return escape(text)
    title_part = escape(text[:idx].strip())
    desc_part = escape(text[idx:].strip())
    return mark_safe(f'{title_part}<br><span class="tows-desc">{desc_part}</span>')
