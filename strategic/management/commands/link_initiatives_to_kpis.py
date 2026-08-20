# -*- coding: utf-8 -*-
"""اتصال پروژه‌های تحول به شاخص کلان/عملیاتی مبنا — بر اساس تطبیق محتوایی دقیق
(عنوان پروژه در برابر عنوان شاخص)، با امتیازدهی وزنی و نرمال‌سازی کاراکتر عربی/
فارسی (ي↔ی). از ۸۰ پروژه‌ی نامزد اولیه، بعد از بررسی دستی کیفیت، ۱۶ مورد که
موضوعاً بی‌ربط بودن (مثلاً «هزینه بازسازی ساختمان تعمیرگاه» که فقط چون هر دو
عبارت «تعمیرگاه مرکزی» داشتن، به یه شاخص کاملاً نامرتبط «درآمد گارانتی» جفت
شده بود) کنار گذاشته شدن."""
from django.core.management.base import BaseCommand
from strategic.models import Initiative, CompanyKPI, OperationalKPI


# (کد پروژه، نوع شاخص، کد شاخص)
PAIRS = [
    ('100EX091', 'operational', 'HR-101-02'),
    ('T121P0124A01', 'operational', 'MT-01-01'),
    ('T121P0125A01', 'operational', 'PP-01-00'),
    ('T121P067A01', 'operational', 'RP-01-02'),
    ('T121P068A01', 'operational', 'C-06-09'), ('T121P068A01', 'operational', 'C-06-08'),
    ('T121P069A01', 'operational', 'C-10-00'), ('T121P069A01', 'operational', 'RP-01-02'),
    ('T121P070A01', 'operational', 'C-10-00'), ('T121P070A01', 'operational', 'HR-78-05'),
    ('T121P071A01', 'company', 'I20'), ('T121P071A01', 'operational', 'C-08-04'),
    ('T121P072A01', 'operational', 'C-06-09'), ('T121P072A01', 'operational', 'C-06-07'),
    ('T121P0140A01', 'operational', 'SP-57-01'), ('T121P0140A01', 'operational', 'EF-01-01'),
    ('T121P086A01', 'operational', 'S-68-02'),
    ('T121P089A01', 'operational', 'S-143-01'), ('T121P089A01', 'operational', 'S-143-02'),
    ('T121P074A01', 'operational', 'RP-02-01'),
    ('T121P079B01', 'company', 'I20'), ('T121P079B01', 'operational', 'C-08-04'),
    ('T121P010A01', 'operational', 'PP-01-00'),
    ('T121P040C01', 'operational', 'E-01-01'),
    ('T121P080B01', 'company', 'I20'), ('T121P080B01', 'operational', 'C-08-04'),
    ('T121P087A01', 'operational', 'S-68-02'),
    ('T121P090A01', 'operational', 'S-143-04'),
    ('T121P011A01', 'operational', 'C-28-00'), ('T121P011A01', 'operational', 'C-11-00'),
    ('100EX128', 'operational', 'E-01-03'),
    ('100EX065', 'operational', 'EF-01-02'), ('100EX065', 'operational', 'SP-57-01'),
    ('100EX035', 'operational', 'SM-10-00'), ('100EX035', 'operational', 'N-36-00'),
    ('100PKK03042', 'company', 'I23'), ('100PKK03042', 'operational', 'C-01-33'),
    ('100PKK03043', 'company', 'I7'), ('100PKK03043', 'company', 'I8'),
    ('100PSH08055', 'operational', 'S-18-01'), ('100PSH08055', 'operational', 'N-16-00'),
    ('100EX002', 'operational', 'S-63-05'), ('100EX002', 'operational', 'S-63-04'),
    ('100EX070', 'operational', 'C-258-13'), ('100EX070', 'operational', 'C-01-37'),
    ('100EX090', 'operational', 'PP-01-00'), ('100EX090', 'operational', 'P-09-00'),
    ('100EX096', 'operational', 'PP-01-05'),
    ('100EX115', 'operational', 'C-258-13'), ('100EX115', 'operational', 'C-01-37'),
    ('100EX117', 'operational', 'SP-70-01'),
    ('100EX138', 'operational', 'C-258-10'), ('100EX138', 'operational', 'C-258-11'),
    ('100EX004', 'operational', 'EF-01-07'),
    ('100EX005', 'operational', 'EF-01-07'),
    ('100EX030', 'operational', 'S-63-05'), ('100EX030', 'operational', 'S-63-04'),
    ('100EX122', 'operational', 'C-01-30'), ('100EX122', 'operational', 'C-06-00'),
    ('100EX125', 'operational', 'EF-01-05'), ('100EX125', 'operational', 'EF-01-06'),
    ('100PKK07005', 'operational', 'C-01-16'), ('100PKK07005', 'operational', 'C-06-03'),
    ('100EX075', 'operational', 'HR-01-11'),
    ('100EX109', 'company', 'I7'), ('100EX109', 'company', 'I8'),
    ('100EX100', 'operational', 'HR-94-01'),
    ('100EX048', 'operational', 'PP-01-07'),
    ('100EX153', 'company', 'I7'), ('100EX153', 'company', 'I8'),
    ('100PKK07019', 'company', 'I7'), ('100PKK07019', 'company', 'I8'),
    ('100PKK01011', 'operational', 'C-02-00'),
    ('100PKK05072', 'operational', 'SP-70-01'),
    ('100PKK01012', 'operational', 'C-02-00'),
    ('100EX039', 'operational', 'PP-01-20'), ('100EX039', 'operational', 'P-10-00'),
    ('100PME03032', 'operational', 'C-258-13'), ('100PME03032', 'operational', 'C-01-37'),
    ('100PKK03046', 'operational', 'SP-70-00'), ('100PKK03046', 'operational', 'C-01-23'),
    ('100PKK05052', 'operational', 'C-06-00'), ('100PKK05052', 'operational', 'C-06-10'),
    ('100EX108', 'operational', 'RP-01-02'),
    ('100EX159', 'operational', 'S-143-05'),
    ('100EX161', 'operational', 'EF-01-07'),
    ('100EX168', 'operational', 'C-02-00'),
    ('100PKA06058', 'operational', 'N-36-00'), ('100PKA06058', 'operational', 'HR-100-27'),
    ('100PKK03031', 'operational', 'C-11-00'), ('100PKK03031', 'operational', 'C-28-00'),
    ('T121P047B01', 'company', 'I16'), ('T121P047B01', 'operational', 'CRM-09-00'),
    ('100EX066', 'operational', 'SP-57-01'), ('100EX066', 'operational', 'EF-01-01'),
    ('100EX147', 'company', 'I20'), ('100EX147', 'operational', 'C-08-04'),
    ('T121P075A01', 'operational', 'C-01-51'), ('T121P075A01', 'operational', 'C-01-09'),
    ('T121P045A01', 'operational', 'PP-01-00'),
    ('T121P033D01', 'operational', 'C-02-00'),
]


class Command(BaseCommand):
    help = "پروژه‌های تحول را به شاخص کلان/عملیاتی مبنای واقعاً مرتبط وصل می‌کند."

    def handle(self, *args, **options):
        init_by_code = {i.code: i for i in Initiative.objects.all()}
        ck_by_code = {k.code: k for k in CompanyKPI.objects.all()}
        opk_by_code = {k.code: k for k in OperationalKPI.objects.all()}

        linked, not_found = 0, []
        for init_code, src_type, kpi_code in PAIRS:
            init = init_by_code.get(init_code)
            if not init:
                not_found.append(f"پروژه {init_code} یافت نشد")
                continue
            if src_type == "company":
                kpi = ck_by_code.get(kpi_code)
                if not kpi:
                    not_found.append(f"شاخص کلان {kpi_code} یافت نشد")
                    continue
                init.source_kpi.add(kpi)
            else:
                kpi = opk_by_code.get(kpi_code)
                if not kpi:
                    not_found.append(f"شاخص عملیاتی {kpi_code} یافت نشد")
                    continue
                init.source_operational_kpi.add(kpi)
            linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط پروژه-شاخص."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
