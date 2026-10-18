# -*- coding: utf-8 -*-
"""ورود اهداف و نتایج کلیدی (OKR) از فایل اکسل به سیستم.

    python manage.py import_okr مسیر/فایل-OKR.xlsx          # جایگزین OKRهای قبلی
    python manage.py import_okr فایل.xlsx --dry-run         # فقط گزارش، بدون ذخیره"""
import openpyxl
from django.core.management.base import BaseCommand, CommandError

from strategic.okr_io import OKRImportError, import_workbook


class Command(BaseCommand):
    help = "ورود OKR (شرکت / معاونت / مدیریت) از اکسل"

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--keep", action="store_true", help="OKRهای موجود را پاک نکن (پیش‌فرض: پاک و جایگزین)")

    def handle(self, *args, **o):
        try:
            wb = openpyxl.load_workbook(o["path"], data_only=True)
            s = import_workbook(wb, keep=o["keep"], dry_run=o["dry_run"])
        except OKRImportError as e:
            raise CommandError(str(e))
        except Exception as e:
            raise CommandError(f"فایل خوانده نشد: {e}")
        self.stdout.write(self.style.SUCCESS(
            f"{'(آزمایشی) ' if o['dry_run'] else ''}اهداف: {s['obj']} — نتایج کلیدی: {s['kr']} — بدون شاخص: {s['nokpi']}"))
