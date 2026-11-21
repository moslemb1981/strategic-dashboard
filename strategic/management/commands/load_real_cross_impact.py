# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from strategic.models import CrossImpactFactor

# منبع: «ماتریس تحلیل اثر متقابل عوامل محیطی تاثیرگذار بر سایپا یدک»
# (مدیریت برنامه‌ریزی و نظارت راهبردی — اسفند ۱۴۰۴)
# دو ناحیه («پیشران‌ها»، «دیده‌بانی») نام‌گذاری‌شده در سند اصلی بودند؛
# دو ناحیه‌ی دیگر («دووجهی»، «نتیجه») طبق تأیید شما با نام رایج MICMAC اضافه شدند.

DATA = {
    "driver": [
        "وضعیت بین‌المللی (سیاسی)",
        "تأمین منابع مالی",
        "نرخ ارز و تورم",
        "قوانین و استانداردها",
    ],
    "relay": [
        "قدرت تأمین‌کنندگان",
    ],
    "watch": [
        "ثبات مدیریت",
        "ناترازی انرژی",
    ],
    "resultant": [
        "نیروی انسانی توانمند",
        "ناآرامی اجتماعی",
        "رفتار مشتریان",
        "قطعات تقلبی",
        "نرخ سرمایه‌گذاری",
        "تغییرات فناوری",
    ],
}


class Command(BaseCommand):
    help = "نتیجه‌ی واقعی تحلیل اثرات متقابل (MICMAC) سایپا یدک را ثبت/به‌روزرسانی می‌کند."

    def handle(self, *args, **options):
        CrossImpactFactor.objects.all().delete()
        total = 0
        for quadrant, items in DATA.items():
            for order, text in enumerate(items, start=1):
                CrossImpactFactor.objects.create(text=text, quadrant=quadrant, order=order)
                total += 1
        self.stdout.write(self.style.SUCCESS(f"{total} عامل واقعی در ۴ ناحیه ثبت شد."))
