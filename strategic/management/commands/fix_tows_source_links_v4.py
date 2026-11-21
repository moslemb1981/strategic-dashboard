# -*- coding: utf-8 -*-
"""اصلاح نهایی ارتباط راهبردهای TOWS «بازرگانی قطعات» بر پایه‌ی شماره‌گذاری
زنده‌ی فعلی سیستم (همون الگویی که برای بسته خدمت، گارانتی خودرو و خدمات
تعمیراتی هم اعمال شد).

نحوه‌ی اجرا (فقط یک‌بار):
    python manage.py fix_tows_source_links_v4
"""
import re
from django.core.management.base import BaseCommand
from strategic.models import TOWSStrategy

FULL_MAP = {'S1': 22, 'S2': 23, 'S3': 24, 'S4': 25, 'S5': 26, 'S6': 27, 'W1': 31, 'W2': 29, 'W3': 28, 'W4': 30, 'W5': 33, 'W6': 35, 'W7': 36, 'W8': 32, 'W9': 34, 'O1': 37, 'O2': 39, 'O3': 38, 'O4': 40, 'O5': 41, 'T1': 43, 'T2': 45, 'T3': 48, 'T4': 49, 'T5': 51, 'T6': 42, 'T7': 44, 'T8': 50, 'T9': 46, 'T10': 47}


class Command(BaseCommand):
    help = "اصلاح نهایی ارتباط source_items راهبردهای TOWS «بازرگانی قطعات» بر پایه‌ی شماره‌گذاری زنده."

    def handle(self, *args, **options):
        fixed, skipped, partial = 0, 0, []
        for obj in TOWSStrategy.objects.filter(business_unit_id=3):
            m = re.search(r"\(([SWOT0-9,+\s]+)\)", obj.text)
            if not m:
                skipped += 1
                continue
            codes = re.findall(r"[SWOT]\d+", m.group(1))
            pks = [FULL_MAP[c] for c in codes if c in FULL_MAP]
            missing = [c for c in codes if c not in FULL_MAP]
            if missing:
                partial.append((obj.pk, missing))
            if not pks:
                skipped += 1
                continue
            obj.source_items.set(pks)
            fixed += 1
        self.stdout.write(self.style.SUCCESS(f"{fixed} راهبرد TOWS «بازرگانی قطعات» اصلاح شد؛ {skipped} مورد رد شد."))
        if partial:
            self.stdout.write(self.style.WARNING("کدهای نامعتبر در خودِ متن:"))
            for pk, missing in partial:
                self.stdout.write(f"  pk={pk} | {missing}")
