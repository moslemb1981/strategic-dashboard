# -*- coding: utf-8 -*-
"""اصلاح نهایی ارتباط راهبردهای TOWS «گارانتی خودرو» و «خدمات تعمیراتی» —
بر پایه‌ی همون شماره‌گذاری زنده‌ای که خودِ سیستم همین الان نمایش می‌ده (که با
فایل اکسل اصلی فرق داشت، چون بعضی آیتم‌های SWOT وزن اهمیت غیرپیش‌فرض دارن و
ترتیب نمایش رو عوض می‌کنن).

نحوه‌ی اجرا (فقط یک‌بار):
    python manage.py fix_tows_source_links_v3
"""
import re
from django.core.management.base import BaseCommand
from strategic.models import TOWSStrategy

BU_MAPS = {'2': {'S1': 132, 'S2': 133, 'S3': 134, 'S4': 135, 'S5': 136, 'S6': 137, 'W1': 139, 'W2': 138, 'W3': 141, 'W4': 140, 'W5': 144, 'W6': 142, 'W7': 143, 'O1': 145, 'O2': 146, 'O3': 148, 'O4': 149, 'O5': 147, 'O6': 150, 'T1': 151, 'T2': 152, 'T3': 154, 'T4': 156, 'T5': 153, 'T6': 155, 'T7': 157, 'T8': 158, 'T9': 159}, '5': {'S1': 106, 'S2': 107, 'S3': 108, 'S4': 110, 'S5': 160, 'S6': 161, 'S7': 162, 'S8': 109, 'S9': 111, 'W1': 113, 'W2': 116, 'W3': 114, 'W4': 163, 'W5': 112, 'W6': 115, 'W7': 117, 'O1': 118, 'O2': 119, 'O3': 120, 'O4': 122, 'O5': 123, 'O6': 164, 'O7': 121, 'T1': 131, 'T2': 124, 'T3': 125, 'T4': 127, 'T5': 128, 'T6': 126, 'T7': 129, 'T8': 130}}


class Command(BaseCommand):
    help = "اصلاح نهایی ارتباط source_items راهبردهای TOWS گارانتی خودرو و خدمات تعمیراتی بر پایه‌ی شماره‌گذاری زنده."

    def handle(self, *args, **options):
        total_fixed, total_skipped, total_partial = 0, 0, []
        for bu_pk_str, full_map in BU_MAPS.items():
            bu_pk = int(bu_pk_str)
            for obj in TOWSStrategy.objects.filter(business_unit_id=bu_pk):
                m = re.search(r"\(([SWOT0-9,+\s]+)\)", obj.text)
                if not m:
                    total_skipped += 1
                    continue
                codes = re.findall(r"[SWOT]\d+", m.group(1))
                pks = [full_map[c] for c in codes if c in full_map]
                missing = [c for c in codes if c not in full_map]
                if missing:
                    total_partial.append((bu_pk, obj.pk, missing))
                if not pks:
                    total_skipped += 1
                    continue
                obj.source_items.set(pks)
                total_fixed += 1

        self.stdout.write(self.style.SUCCESS(f"{total_fixed} راهبرد TOWS اصلاح شد؛ {total_skipped} مورد رد شد."))
        if total_partial:
            self.stdout.write(self.style.WARNING("موارد با کد نامعتبر در خودِ متن (نیاز به اصلاح دستی متن):"))
            for bu_pk, pk, missing in total_partial:
                self.stdout.write(f"  کسب‌وکار {bu_pk} | pk={pk} | کدهای نامعتبر: {missing}")
