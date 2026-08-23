# -*- coding: utf-8 -*-
"""میان‌افزار ثبت بازدید کاربران — برای هر صفحه‌ای که یه کاربر واقعی می‌بینه
(نه فایل‌های استاتیک مثل CSS/JS/عکس)، یه خط توی logs/users.log ثبت می‌کنه:
تاریخ و ساعت، مسیر صفحه، آی‌پی، نام سیستمی مربوط به اون آی‌پی (در صورت امکان)،
و نام کاربری (در صورت لاگین‌بودن)."""
import logging
import socket

user_log = logging.getLogger("user_visits")

# پسوندهایی که نباید لاگ بشن (فایل‌های استاتیک، نه بازدید واقعی صفحه)
SKIP_EXTENSIONS = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico",
    ".woff", ".woff2", ".ttf", ".eot", ".map", ".json",
)
SKIP_PREFIXES = ("/static/", "/media/")

# کش ساده‌ی حافظه‌ای برای جلوگیری از جست‌وجوی نام سیستمی تکراری برای یه آی‌پی
_hostname_cache = {}


def _resolve_hostname(ip):
    """نام سیستمی مربوط به یه آی‌پی رو پیدا می‌کنه. اول با DNS معکوس امتحان
    می‌کنه؛ اگه جواب نداد (که روی شبکه‌های داخلی ویندوزی برای بعضی سیستم‌ها
    معموله، چون رکورد PTR ثبت نشده)، با getfqdn هم یه بار دیگه امتحان می‌کنه.
    نتیجه (موفق یا ناموفق) کش می‌شه تا برای درخواست‌های بعدی از همون آی‌پی،
    دوباره منتظر نمونیم."""
    if ip in _hostname_cache:
        return _hostname_cache[ip]
    hostname = "—"
    try:
        socket.setdefaulttimeout(1.5)
        hostname, _, _ = socket.gethostbyaddr(ip)
    except Exception:
        try:
            fqdn = socket.getfqdn(ip)
            if fqdn and fqdn != ip:
                hostname = fqdn
        except Exception:
            pass
    finally:
        socket.setdefaulttimeout(None)
    _hostname_cache[ip] = hostname
    return hostname


def _get_client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "—")


class UserVisitLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path
        if path.startswith(SKIP_PREFIXES) or path.endswith(SKIP_EXTENSIONS):
            return response

        ip = _get_client_ip(request)
        hostname = _resolve_hostname(ip)
        username = request.user.username if getattr(request, "user", None) and request.user.is_authenticated else "—"

        user_log.info(f"path={path} | ip={ip} | host={hostname} | user={username}")
        return response
