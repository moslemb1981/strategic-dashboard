# -*- coding: utf-8 -*-
"""اتصال پروژه‌های «بازرگانی قطعات» به راهبردهای TOWS واقعاً مرتبط — بر اساس
تطبیق محتوایی دقیق (نرمال‌شده و بررسی‌شده دستی) بین عنوان پروژه و متن کامل
راهبرد. فقط ۸ تطابق قوی از ۱۷ نامزد اولیه نگه داشته شد؛ ۹ مورد که فقط روی
کلمات عمومی (مثل «بهره‌گیری» یا «سازی/رسانی») جفت شده بودن، کنار گذاشته شدن."""
from django.core.management.base import BaseCommand
from strategic.models import Initiative, TOWSStrategy


# (کد پروژه، شناسه‌ی راهبرد TOWS)
PAIRS = [
    ("T121P0141A01", 21),
    ("T121P0108C01", 27),
    ("100EX067", 22),
    ("100EX137", 22),
    ("100PKK07068", 13),
    ("100EX005", 19),
    ("100EX122", 15),
    ("100EX136", 22),
]


class Command(BaseCommand):
    help = "پروژه‌های بازرگانی قطعات را به راهبردهای TOWS واقعاً مرتبط وصل می‌کند."

    def handle(self, *args, **options):
        init_by_code = {i.code: i for i in Initiative.objects.all()}
        linked, not_found = 0, []
        for code, tows_pk in PAIRS:
            init = init_by_code.get(code)
            if not init:
                not_found.append(f"پروژه {code} یافت نشد")
                continue
            try:
                tows = TOWSStrategy.objects.get(pk=tows_pk)
            except TOWSStrategy.DoesNotExist:
                not_found.append(f"راهبرد {tows_pk} یافت نشد")
                continue
            init.source_tows.add(tows)
            linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط پروژه-TOWS."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
