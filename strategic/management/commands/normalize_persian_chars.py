"""یکسان‌سازی حروف عربی در متن‌های سیستم: «ي» ← «ی»، «ك» ← «ک» (و «ى» ← «ی»).

علت نقطه‌ی زیر «ی» آخر کلمه: حرف عربی «ي» (U+064A) در آخر کلمه دو نقطه دارد، ولی «ی» فارسی (U+06CC) ندارد.
جستجو/جایگزینی در اکسل این دو را یکی می‌گیرد، برای همین Find & Replace اثری نداشت.

    python manage.py normalize_persian_chars            # فقط گزارش
    python manage.py normalize_persian_chars --apply    # اعمال (قبلش از db.sqlite3 پشتیبان بگیرید)
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import models, transaction

MAP = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک"})
SKIP_FIELDS = {"password"}


def fix(text):
    return text.translate(MAP) if isinstance(text, str) else text


class Command(BaseCommand):
    help = "تبدیل حروف عربی «ي» و «ك» به «ی» و «ک» در همه‌ی متن‌های برنامه (پیش‌فرض: فقط گزارش)"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **opts):
        total_rows, report = 0, []
        with transaction.atomic():
            for model in apps.get_app_config("strategic").get_models():
                fields = [f for f in model._meta.concrete_fields
                          if isinstance(f, (models.CharField, models.TextField)) and not f.choices
                          and f.name not in SKIP_FIELDS]
                for f in fields:
                    n = 0
                    for pk, val in model.objects.exclude(**{f.name: ""}).values_list("pk", f.name):
                        new = fix(val)
                        if new != val:
                            n += 1
                            if opts["apply"]:
                                model.objects.filter(pk=pk).update(**{f.name: new})
                    if n:
                        report.append((f"{model.__name__}.{f.name}", n))
                        total_rows += n
            if not opts["apply"]:
                transaction.set_rollback(True)
        for name, n in report:
            self.stdout.write(f"{name}: {n}")
        if opts["apply"]:
            self.stdout.write(self.style.SUCCESS(f"انجام شد: {total_rows} مقدار اصلاح شد."))
        else:
            self.stdout.write(f"حالت گزارش: {total_rows} مقدار اصلاح می‌شود. برای اعمال --apply را اضافه کنید.")
