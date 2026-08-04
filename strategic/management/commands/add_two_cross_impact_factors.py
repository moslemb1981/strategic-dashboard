# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from strategic.models import CrossImpactFactor

# دو عامل جدید که به ۱۳ عامل قبلی اضافه می‌شوند.
# برخلاف load_real_cross_impact.py، این دستور چیزی را پاک نمی‌کند —
# فقط این دو مورد را (اگر از قبل نبودند) اضافه می‌کند، تا امتیازهای
# قبلاً ثبت‌شده در ماتریس اثر متقابل دست‌نخورده بمانند.
# ناحیه‌ی «دیده‌بانی» فقط موقتی است؛ بعد از وارد کردن امتیاز این دو
# عامل با بقیه در «ماتریس ورودی و محاسبه»، ناحیه‌ی واقعی را با دکمه‌ی
# «اعمال پیشنهادها» به‌روزرسانی کنید.

NEW_FACTORS = [
    "الزامات کنشی و واکنشی مدیریت پسماند",
    "استانداردهای مدیریتی",
]


class Command(BaseCommand):
    help = "دو عامل جدید را به ماتریس اثر متقابل اضافه می‌کند، بدون حذف عوامل/امتیازهای موجود."

    def handle(self, *args, **options):
        start_order = (CrossImpactFactor.objects.count()) + 1
        added = 0
        for i, text in enumerate(NEW_FACTORS):
            obj, created = CrossImpactFactor.objects.get_or_create(
                text=text,
                defaults={"quadrant": "watch", "order": start_order + i},
            )
            if created:
                added += 1
                self.stdout.write(self.style.SUCCESS(f"اضافه شد: {text}"))
            else:
                self.stdout.write(self.style.WARNING(f"از قبل موجود بود، رد شد: {text}"))
        self.stdout.write(self.style.SUCCESS(f"پایان: {added} عامل جدید اضافه شد."))
