# -*- coding: utf-8 -*-
"""بارگذاری بانک کامل شاخص‌های عملیاتی سازمان (۲۴۲ شاخص، طبق فایل رسمی شرکت)."""
import os
from django.core.management.base import BaseCommand
from strategic.models import OperationalKPI

DATA_FILE = os.path.join(os.path.dirname(__file__), "_operational_kpi_data.txt")


class Command(BaseCommand):
    help = "بانک کامل شاخص‌های عملیاتی سازمان را از فایل داده بارگذاری می‌کند."

    def handle(self, *args, **options):
        if not os.path.exists(DATA_FILE):
            self.stdout.write(self.style.ERROR(f"فایل داده پیدا نشد: {DATA_FILE}"))
            return

        created, updated, order = 0, 0, 0
        with open(DATA_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) not in (4, 5):
                    continue
                if len(parts) == 5:
                    code, title, unit, department, domain = [p.strip() for p in parts]
                else:
                    code, title, unit, department = [p.strip() for p in parts]
                    domain = "Q"
                order += 1
                _, was_created = OperationalKPI.objects.update_or_create(
                    code=code,
                    defaults=dict(title=title, unit=unit, department=department, domain=domain, order=order),
                )
                created += 1 if was_created else 0
                updated += 0 if was_created else 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {created} شاخص جدید، {updated} به‌روزرسانی‌شده."))
