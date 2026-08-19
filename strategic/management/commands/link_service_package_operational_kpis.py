# -*- coding: utf-8 -*-
"""اتصال کارت‌های نقشه استراتژیک «بسته خدمت» به شاخص‌های عملیاتی مرتبط —
بر اساس تحلیل محتوایی، فقط جاهایی که تطابق روشن بود."""
from django.core.management.base import BaseCommand
from strategic.models import StrategicObjective, OperationalKPI, BusinessUnit


# (کد کارت، [کدهای شاخص عملیاتی مرتبط])
KPI_LINKS = [
    ("F1", ["SP-214-00"]),
    # سود عملیاتی بسته خدمت ← حاشیه سود ناخالص بسته خدمت (تطابق مستقیم)

    ("F3", ["S-40-00", "S-43-00"]),
    # استراتژی رشد ← فروش ریالی و تعدادی کارت طلایی (رشد درآمد و رشد حجم)

    ("F5", ["S-18-01", "N-16-00"]),
    # استفاده حداکثری از ظرفیت سازمان/شبکه ← بهره‌وری ایستگاه‌های تعمیرگاه مرکزی + بهره‌وری ایستگاه‌های نمایندگی‌ها

    ("C2", ["S-20-00", "CRM-04-00"]),
    # خدمات باکیفیت ← رضایت مشتریان از بسته خدمت + نرخ شکایت از خدمات پس از فروش

    ("C4", ["S-68-01", "S-68-02"]),
    # حفظ مشتریان موجود ← تمدید بسته خدمت (کارکرده و نو) — دقیقاً معیار نرخ نگهداشت مشتری

    ("P1", ["S-41-00", "S-41-01"]),
    # ارائه بسته‌های خدمت متنوع ← فروش کارت طلایی به تفکیک نوع (اختیاری نو / کارکرده)

    ("P10", ["N-109-00"]),
    # توسعه کسب‌وکار شبکه ← رضایت نمایندگی‌ها از فرایند بسته خدمت (DSI)

    ("L1", ["HR-100-27", "HR-100-05", "HR-100-20"]),
    # توسعه رویکرد شایستگی‌محور، مشاغل، جانشین‌پروری و شایسته‌گزینی ←
    # میزان انطباق شایستگی کارکنان + انطباق شرایط احراز (جذب) + انطباق شرایط احراز (پست)

    ("L4", ["crm-02-00"]),
    # توسعه فرهنگ مشتری‌مداری و بهبود مستمر ← رضایت مشتریان از نحوه رسیدگی به شکایات (پیامد فرهنگ مشتری‌مداری)

    ("L6", ["N-36-01", "N-36-00"]),
    # انتقال دانش به ذی‌نفعان اصلی ← درصد حضور پرسنل نمایندگی در آموزش + اثربخشی آموزش ارائه‌شده به شبکه
]


class Command(BaseCommand):
    help = "کارت‌های نقشه استراتژیک بسته خدمت را به شاخص‌های عملیاتی مرتبط وصل می‌کند."

    def handle(self, *args, **options):
        bu = BusinessUnit.objects.get(name__icontains="بسته خدمت")
        kpi_by_code = {k.code: k for k in OperationalKPI.objects.all()}

        linked, not_found = 0, []
        for card_code, kpi_codes in KPI_LINKS:
            try:
                obj = StrategicObjective.objects.get(business_unit=bu, code=card_code)
            except StrategicObjective.DoesNotExist:
                not_found.append(f"کارت {card_code} یافت نشد")
                continue
            obj.linked_operational_kpis.clear()
            for kpi_code in kpi_codes:
                kpi = kpi_by_code.get(kpi_code)
                if not kpi:
                    not_found.append(f"شاخص {kpi_code} یافت نشد")
                    continue
                obj.linked_operational_kpis.add(kpi)
                linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط شاخص عملیاتی."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
