# -*- coding: utf-8 -*-
"""اصلاح نهایی ارتباط راهبردهای TOWS «بسته خدمت» — این‌بار بر پایه‌ی همون
شماره‌گذاری زنده‌ای که خودِ سیستم همین الان نمایش می‌ده (نه فایل اکسل اصلی)،
چون این دو تا با هم فرق داشتن (ترتیب نمایش سیستم بر پایه‌ی وزن اهمیت مرتب
می‌شه، نه لزوماً همون ترتیب فایل اصلی).

نحوه‌ی اجرا (فقط یک‌بار):
    python manage.py fix_tows_source_links_v2
"""
import re
from django.core.management.base import BaseCommand
from strategic.models import TOWSStrategy

# نگاشت «کد نمایشی زنده‌ی فعلی سیستم -> شناسه‌ی دیتابیس» برای «بسته خدمت»
FULL_MAP = {'S1': 78, 'S2': 79, 'S3': 80, 'S4': 82, 'S5': 83, 'W1': 87, 'W2': 85, 'W3': 84, 'W4': 86, 'W5': 165, 'W6': 166, 'W7': 167, 'W8': 168, 'W9': 88, 'O1': 93, 'O2': 91, 'O3': 92, 'O4': 94, 'T1': 96, 'T2': 98, 'T3': 102, 'T4': 105, 'T5': 95, 'T6': 97, 'T7': 101, 'T8': 103, 'T9': 99, 'T10': 100, 'T11': 104}


class Command(BaseCommand):
    help = "اصلاح نهایی ارتباط source_items راهبردهای TOWS «بسته خدمت» بر پایه‌ی شماره‌گذاری زنده‌ی فعلی سیستم."

    def handle(self, *args, **options):
        fixed, skipped = 0, 0
        for obj in TOWSStrategy.objects.filter(business_unit_id=1):
            m = re.search(r"\(([SWOT0-9,+\s]+)\)", obj.text)
            if not m:
                skipped += 1
                continue
            codes = re.findall(r"[SWOT]\d+", m.group(1))
            pks = [FULL_MAP[c] for c in codes if c in FULL_MAP]
            if not pks:
                skipped += 1
                continue
            obj.source_items.set(pks)
            fixed += 1
        self.stdout.write(self.style.SUCCESS(f"{fixed} راهبرد TOWS «بسته خدمت» بر پایه‌ی شماره‌گذاری زنده اصلاح شد؛ {skipped} مورد رد شد."))
