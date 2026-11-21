# -*- coding: utf-8 -*-
"""پیشنهاد اولیه‌ی اتصال ۸ ارزش سازمانی به اهداف استراتژیک مرتبط (از هر ۵ کسب‌وکار) —
بر اساس تحلیل محتوایی. طبق توافق، این یه نقطه‌ی شروعه؛ قابل‌اصلاح دستی بعداً."""
from django.core.management.base import BaseCommand
from strategic.models import OrgValue, StrategicObjective


# (متن ارزش، [شناسه‌ی هدف استراتژیک])
VALUE_LINKS = [
    ("رقابت سالم", [8, 102]),
    # C1 قیمت مناسب نسبت به شبکه و بازار (بسته خدمت) + P22 مبارزه با قاچاق و تقلب (بازرگانی قطعات)

    ("شفافیت و اعتمادآفرینی", [96, 82]),
    # P16 شفاف‌سازی و تسهیل برگشت از فروش/خرید + P2 اعتماد و هوشمندسازی مدیریت پرداخت ارزش (بازرگانی قطعات)

    ("کرامت انسانی ناظر بر حقوق ذی‌نفعان", [168, 103]),
    # P13 ایمنی/بهداشت کارکنان و مشتریان (تعمیراتی) + P23 ایمنی و بهداشت شغلی (بازرگانی قطعات)

    ("اطلاع‌رسانی جامع به ذی‌نفعان", [130, 163]),
    # P7 آگاهی‌بخشی به مشتریان از قابلیت‌ها (آپشن) + P8 آگاهی از نیازها و انتظارات مشتریان (تعمیراتی)

    ("توان‌افزایی و توسعه قابلیت‌های کارکنان", [27, 62, 105, 137, 171]),
    # L1 توسعه رویکرد شایستگی‌محور — از هر ۵ کسب‌وکار (تطابق مستقیم و کامل)

    ("نوآوری بازار محور", [75, 119]),
    # C2 نوآوری در پلتفرم ثابت — بازرگانی قطعات + آپشن

    ("وحدت و کارتیمی", [88]),
    # P8 هم‌افزایی تولیدکنندگان گروه (بازرگانی قطعات)

    ("مشتری‌مداری", [30, 177, 110, 142]),
    # L4 توسعه فرهنگ مشتری‌مداری (بسته خدمت) + L7 همان (تعمیراتی) + L6 مشتری‌محوری (بازرگانی قطعات + آپشن)
]


class Command(BaseCommand):
    help = "پیشنهاد اولیه‌ی اتصال ارزش‌های سازمانی به اهداف استراتژیک مرتبط را ثبت می‌کند."

    def handle(self, *args, **options):
        linked, not_found = 0, []
        for value_text, obj_ids in VALUE_LINKS:
            try:
                value = OrgValue.objects.get(text=value_text)
            except OrgValue.DoesNotExist:
                not_found.append(f"ارزش «{value_text}» یافت نشد")
                continue
            value.related_objectives.clear()
            for obj_id in obj_ids:
                obj = StrategicObjective.objects.filter(pk=obj_id).first()
                if not obj:
                    not_found.append(f"هدف با شناسه {obj_id} یافت نشد")
                    continue
                value.related_objectives.add(obj)
                linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط روی {len(VALUE_LINKS)} ارزش سازمانی."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
