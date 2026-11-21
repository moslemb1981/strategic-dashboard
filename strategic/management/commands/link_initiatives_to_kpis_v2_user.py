# -*- coding: utf-8 -*-
"""اتصال پروژه‌های تحول به شاخص عملیاتی مبنا — دور دوم، بر اساس بررسی دقیق و
دستی خودِ کاربر (نه تحلیل خودکار). این لیست را کاربر شخصاً پروژه به پروژه
بررسی و تأیید کرده — بدون نیاز به بررسی کیفیت اضافه از سمت ما.

⚠️ این دستور «تفاضلی» است — یعنی حتی اگه بعضی از این جفت‌ها قبلاً (از طریق
دستور link_initiatives_to_kpis) ثبت شده باشن، دوباره اجرا کردنش مشکلی ایجاد
نمی‌کنه (M2M.add روی مورد تکراری، خطا نمی‌ده)."""
from django.core.management.base import BaseCommand
from strategic.models import Initiative, OperationalKPI


# (کد پروژه، کد شاخص عملیاتی) — همگی از منبع «شاخص عملیاتی» هستن
PAIRS = [
    ('T121P0124A01', 'MT-01-01'), ('T121P068A01', 'C-06-08'), ('T121P068A01', 'C-06-09'),
    ('T121P069A01', 'C-10-00'), ('T121P070A01', 'C-10-00'), ('T121P070A01', 'HR-78-05'),
    ('T121P070A01', 'HR-78-15'), ('T121P072A01', 'C-06-07'), ('T121P072A01', 'C-06-09'),
    ('T121P0140A01', 'SP-57-01'), ('T121P0140A01', 'EF-01-09'), ('T121P0140A01', 'EF-01-07'),
    ('T121P0140A01', 'EF-01-06'), ('T121P0140A01', 'EF-01-05'),
    ('T121P077A01', 'C-01-20'), ('T121P077A01', 'MT-01-01'), ('T121P077A01', 'C-258-13'),
    ('T121P077A01', 'C-01-37'), ('T121P077A01', 'MT-01-00'),
    ('T121P033D01', 'C-02-00'), ('T121P0147A01', 'RC-01-00'), ('T121P078A01', 'RP-01-01'),
    ('100PKA03008', 'PP-01-06'), ('100EX065', 'EF-01-09'), ('100EX065', 'EF-01-02'),
    ('100EX033', 'S-143-00'), ('100PKK03043', 'S-43-00'), ('100PKK03043', 'S-43-01'),
    ('100PSH08055', 'N-16-00'), ('100EX066', 'SP-57-01'), ('100EX066', 'EF-01-09'),
    ('100EX066', 'EF-01-01'), ('100EX066', 'EF-01-07'), ('100EX066', 'EF-01-06'),
    ('100EX115', 'C-258-13'), ('100EX030', 'S-63-05'), ('100EX030', 'S-63-04'),
    ('100EX030', 'S-63-03'), ('100EX031', 'S-143-07'), ('100EX125', 'EF-01-09'),
    ('100PKK07005', 'C-01-16'), ('100PKK01012', 'C-02-00'),
    ('100EX134', 'C-258-13'), ('100EX134', 'C-261-20'), ('100EX134', 'C-261-10'),
    ('100EX134', 'C-261-01'), ('100EX134', 'C-258-03'),
    ('100EX150', 'C-28-00'), ('100EX150', 'C-11-00'),
    ('100PKK03046', 'SP-70-00'),
    ('100EX160', 'C-258-12'), ('100EX160', 'C-01-36'), ('100EX160', 'SP-215-01'),
    ('100EX160', 'C-258-10'), ('100EX160', 'C-01-34'),
    ('100EX161', 'EF-01-07'), ('100EX167', 'S-07-00'), ('100EX168', 'C-02-00'),
]


class Command(BaseCommand):
    help = "پروژه‌های تحول را به شاخص عملیاتی مبنا وصل می‌کند (بررسی و تأیید دستی کاربر)."

    def handle(self, *args, **options):
        init_by_code = {i.code: i for i in Initiative.objects.all()}
        opk_by_code = {k.code: k for k in OperationalKPI.objects.all()}

        linked, already, not_found = 0, 0, []
        for init_code, kpi_code in PAIRS:
            init = init_by_code.get(init_code)
            opk = opk_by_code.get(kpi_code)
            if not init:
                not_found.append(f"پروژه {init_code} یافت نشد")
                continue
            if not opk:
                not_found.append(f"شاخص {kpi_code} یافت نشد")
                continue
            if opk in init.source_operational_kpi.all():
                already += 1
            else:
                init.source_operational_kpi.add(opk)
                linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط جدید."))
        self.stdout.write(f"از قبل موجود بود: {already} مورد.")
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
