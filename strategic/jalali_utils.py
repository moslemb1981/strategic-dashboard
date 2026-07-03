import datetime
import jdatetime

PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹"


def _normalize_digits(s):
    for i, d in enumerate(PERSIAN_DIGITS):
        s = s.replace(d, str(i))
    return s


def gregorian_to_jalali_str(g_date):
    """Takes a Python date/datetime, returns 'YYYY/MM/DD' in Jalali (Persian digits)."""
    if not g_date:
        return ""
    if isinstance(g_date, datetime.datetime):
        g_date = g_date.date()
    j = jdatetime.date.fromgregorian(date=g_date)
    latin = j.strftime("%Y/%m/%d")
    return "".join(PERSIAN_DIGITS[int(ch)] if ch.isdigit() else ch for ch in latin)


def jalali_str_to_gregorian(j_str):
    """Parses a Jalali date string like '1405/04/12' or '۱۴۰۵/۰۴/۱۲' and returns a Python date."""
    j_str = _normalize_digits((j_str or "").strip())
    if not j_str:
        return None
    parts = j_str.replace("-", "/").split("/")
    if len(parts) != 3:
        raise ValueError("فرمت تاریخ نامعتبر است — به‌صورت ۱۴۰۵/۰۴/۱۲ وارد کنید")
    y, m, d = (int(p) for p in parts)
    return jdatetime.date(y, m, d).togregorian()


def jalali_today_str():
    latin = jdatetime.date.today().strftime("%Y/%m/%d")
    return "".join(PERSIAN_DIGITS[int(ch)] if ch.isdigit() else ch for ch in latin)
