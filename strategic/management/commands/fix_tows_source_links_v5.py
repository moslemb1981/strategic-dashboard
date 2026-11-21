# -*- coding: utf-8 -*-
"""اصلاح نهایی ارتباط راهبردهای TOWS «آپشن» بر پایه‌ی شماره‌گذاری زنده‌ی
فعلی سیستم (همون الگوی بندهای ۲۵۸ و ۲۵۹).

نحوه‌ی اجرا (فقط یک‌بار):
    python manage.py fix_tows_source_links_v5
"""
import re
from django.core.management.base import BaseCommand
from strategic.models import TOWSStrategy

FULL_MAP = {'S1': 55, 'S2': 56, 'S3': 54, 'S4': 57, 'S5': 58, 'W1': 61, 'W2': 62, 'W3': 63, 'W4': 59, 'W5': 60, 'O1': 64, 'O2': 65, 'O3': 66, 'O4': 67, 'O5': 68, 'T1': 69, 'T2': 72, 'T3': 70, 'T4': 71, 'T5': 74, 'T6': 76, 'T7': 77, 'T8': 73, 'T9': 75}


class Command(BaseCommand):
    help = "اصلاح نهایی ارتباط source_items راهبردهای TOWS «آپشن» بر پایه‌ی شماره‌گذاری زنده."

    def handle(self, *args, **options):
        fixed, skipped, partial = 0, 0, []
        for obj in TOWSStrategy.objects.filter(business_unit_id=4):
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
        self.stdout.write(self.style.SUCCESS(f"{fixed} راهبرد TOWS «آپشن» اصلاح شد؛ {skipped} مورد رد شد."))
        if partial:
            self.stdout.write(self.style.WARNING("کدهای نامعتبر در خودِ متن:"))
            for pk, missing in partial:
                self.stdout.write(f"  pk={pk} | {missing}")
