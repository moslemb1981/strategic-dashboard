# -*- coding: utf-8 -*-
"""اتصال کارت‌های نقشه استراتژیک «بازرگانی قطعات» به راهبرد TOWS مبنا و شاخص‌های
استراتژیک (I1-I26) مرتبط — بر اساس تحلیل محتوایی، فقط جاهایی که تطابق روشن بود."""
from django.core.management.base import BaseCommand
from strategic.models import StrategicObjective, TOWSStrategy, CompanyKPI, BusinessUnit


# (pk هدف، pk راهبرد TOWS یا None)
TOWS_LINKS = [
    (76, 17),   # کانال توزیع مناسب ← تمرکززدایی از شبکه توزیع/هاب منطقه‌ای
    (68, 22),   # استراتژی بهره‌وری ← بهره‌وری اشتراکی لجستیک
    (84, 19),   # تعیین تکلیف اقلام مازاد ← چابک‌سازی موجودی، جلوگیری از انجماد سرمایه
    (87, 14),   # جذب/حفظ تولیدکنندگان و واردکنندگان ← بهره‌گیری از ظرفیت آزاد تأمین‌کنندگان
    (88, 14),   # هم‌افزایی تولیدکنندگان گروه ← همان
    (89, 14),   # خدمات و مزایا به تولیدکنندگان/واردکنندگان ← همان
    (101, 16),  # توسعه استانداردهای اجباری قطعات ← صیانت از برند در برابر قطعات تقلبی
    (102, 16),  # همکاری با دولت درباره قاچاق/تقلب ← همان
]

# (pk هدف، [کدهای KPI مرتبط])
KPI_LINKS = [
    (78, ["I1", "I2"]),   # رشد سریع فروشگاه‌ها/تعمیرگاه‌ها/مشتریان بزرگ
    (71, ["I1", "I2"]),   # درآمد مستقیم از فروشگاه‌ها/تعمیرکاران/مشتریان جدید
    (85, ["I16"]),        # تعیین بر اساس MRP ← نرخ گردش موجودی شرکت
]


class Command(BaseCommand):
    help = "کارت‌های نقشه استراتژیک بازرگانی قطعات را به TOWS مبنا و KPI مرتبط وصل می‌کند."

    def handle(self, *args, **options):
        kpi_by_code = {}
        for k in CompanyKPI.objects.all():
            if k.code:
                kpi_by_code[k.code.strip().upper()] = k

        tows_linked, not_found = 0, []
        for obj_pk, tows_pk in TOWS_LINKS:
            updated = StrategicObjective.objects.filter(pk=obj_pk).update(source_tows_id=tows_pk)
            tows_linked += updated
            if not updated:
                not_found.append(f"هدف {obj_pk} یافت نشد")

        kpi_linked = 0
        for obj_pk, codes in KPI_LINKS:
            try:
                obj = StrategicObjective.objects.get(pk=obj_pk)
            except StrategicObjective.DoesNotExist:
                not_found.append(f"هدف {obj_pk} یافت نشد")
                continue
            for code in codes:
                kpi = kpi_by_code.get(code.upper())
                if not kpi:
                    not_found.append(f"KPI با کد {code} یافت نشد")
                    continue
                obj.linked_kpis.add(kpi)
                kpi_linked += 1

        self.stdout.write(self.style.SUCCESS(
            f"ثبت شد: {tows_linked} ارتباط TOWS و {kpi_linked} ارتباط KPI."
        ))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
