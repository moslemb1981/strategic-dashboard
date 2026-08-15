# -*- coding: utf-8 -*-
"""بارگذاری آرشیو عوامل شناسایی‌شده‌ی اولیه (قبل از پالایش) کل سازمان."""
import os
from django.core.management.base import BaseCommand
from strategic.models import RawIdentifiedFactor

DATA_FILE = os.path.join(os.path.dirname(__file__), "_raw_factors_data.txt")


class Command(BaseCommand):
    help = "آرشیو ۵۲۵ عامل شناسایی‌شده‌ی اولیه (PESTEL+Porter) را از فایل داده بارگذاری می‌کند."

    def handle(self, *args, **options):
        if not os.path.exists(DATA_FILE):
            self.stdout.write(self.style.ERROR(f"فایل داده پیدا نشد: {DATA_FILE}"))
            return

        RawIdentifiedFactor.objects.all().delete()
        objs = []
        row_counters = {"pestel": 0, "porter": 0}
        with open(DATA_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.rstrip("\n")
                if not line.strip():
                    continue
                parts = line.split("|")
                if len(parts) != 4:
                    continue
                source_type, department, category, text = parts
                row_counters[source_type] += 1
                objs.append(RawIdentifiedFactor(
                    source_type=source_type, department=department, category=category,
                    text=text, row_number=row_counters[source_type],
                ))

        RawIdentifiedFactor.objects.bulk_create(objs)
        self.stdout.write(self.style.SUCCESS(
            f"ثبت شد: {len(objs)} عامل خام ({row_counters['pestel']} PESTEL + {row_counters['porter']} Porter)."
        ))
