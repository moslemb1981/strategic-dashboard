# -*- coding: utf-8 -*-
"""اتصال موارد SWOT و ریسک‌های مرتبط با سناریوی «هوای مه‌آلود» بر اساس تحلیل محتوایی متن
واقعی این سناریو (طبق تأیید کاربر)."""
from django.core.management.base import BaseCommand
from strategic.models import Scenario, SWOTItem, Risk


SWOT_PKS = [
    72, 156,        # تحریم‌های بین‌المللی
    45, 70,         # تورم / نوسان نرخ ارز
    44, 97, 76, 126, 153,  # ناترازی انرژی
    128, 154, 77,   # خروج نیروی انسانی/سرمایه انسانی
    43, 96,         # نقدینگی / مالی مسدود
    51, 105,        # مواد اولیه فولاد/پتروشیمی
    42, 95,         # قطعات تقلبی/غیراصلی
    125,            # کاهش قدرت خرید مشتری
    124,            # مهاجرت به تعمیرگاه آزاد
]

RISK_PKS = [26, 23, 20, 21, 19]


class Command(BaseCommand):
    help = "موارد SWOT و ریسک‌های مرتبط با سناریوی «هوای مه‌آلود» را وصل می‌کند."

    def handle(self, *args, **options):
        foggy = Scenario.objects.get(quadrant="foggy")

        swot_linked = 0
        for pk in SWOT_PKS:
            updated = SWOTItem.objects.filter(pk=pk).update(source_scenario=foggy)
            swot_linked += updated

        risk_linked = 0
        for pk in RISK_PKS:
            try:
                risk = Risk.objects.get(pk=pk)
            except Risk.DoesNotExist:
                continue
            if not risk.related_scenario.filter(pk=foggy.pk).exists():
                risk.related_scenario.add(foggy)
                risk_linked += 1

        self.stdout.write(self.style.SUCCESS(
            f"ثبت شد: {swot_linked} مورد SWOT و {risk_linked} ریسک به سناریوی «هوای مه‌آلود» وصل شد."
        ))
