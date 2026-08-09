# -*- coding: utf-8 -*-
"""
اتصال ۱۵ عامل «ماتریس اثر متقابل» (MICMAC) به عامل PESTEL یا نیروی Porter معادلشان.
این عوامل چکیده‌شده‌اند (نه لزوماً کپی دقیق متن)، پس تطبیق بر اساس شناسه‌ی دستی و
تحلیل‌شده انجام می‌شود، نه تطبیق متنی خودکار.

⚠️ چند مورد (مشخص‌شده در کامنت) «نماینده‌ی کلی» یک نیرو/دسته‌اند، نه معادل دقیق —
چون مدل فقط اجازه‌ی یک ارتباط PESTEL و یک ارتباط Porter به‌ازای هر عامل را می‌دهد.
"""
from django.core.management.base import BaseCommand
from strategic.models import CrossImpactFactor, PestelFactor, PorterForce


# (متن دقیق عامل ماتریس، نوع منبع، pk منبع)
LINKS = [
    ("ارتباطات بین‌المللی", "pestel", 51),
    ("تأمین منابع مالی", "pestel", 57),
    ("تغییرات نرخ ارز و تورم", "pestel", 58),
    ("قوانین و استانداردها", "pestel", 81),
    ("قدرت تأمین‌کنندگان", "porter", 15),       # نماینده‌ی کلی نیروی تأمین‌کنندگان
    ("ناترازی منابع انرژی", "pestel", 76),
    ("نیروی انسانی توانمند", "pestel", 62),
    ("ناآرامی اجتماعی", "pestel", 63),
    ("رفتار مشتریان", "pestel", 59),
    ("قطعات غیراصلی", "porter", 27),
    ("نرخ سرمایه‌گذاری", "porter", 28),
    ("تغییرات فناوری", "pestel", 74),           # نماینده‌ی کلی روند فناوری
    ("الزامات کنشی و واکنشی مدیریت پسماند", "pestel", 80),
    ("استانداردهای مدیریتی", "pestel", 87),
    # «ثبات مدیریت» عمداً وصل نشد — هیچ عامل PESTEL/Porter متناظری ندارد.
]


class Command(BaseCommand):
    help = "عوامل ماتریس اثر متقابل را به عامل PESTEL/نیروی Porter معادلشان وصل می‌کند."

    def handle(self, *args, **options):
        linked, not_found = 0, []
        for text, source_type, pk in LINKS:
            factor = CrossImpactFactor.objects.filter(text=text).first()
            if not factor:
                not_found.append(text)
                continue
            if source_type == "pestel":
                factor.linked_pestel_id = pk
            else:
                factor.linked_porter_id = pk
            factor.save()
            linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} عامل ماتریس اثر متقابل وصل شد."))
        if not_found:
            self.stdout.write(self.style.WARNING("یافت نشد:"))
            for t in not_found:
                self.stdout.write("  - " + t)
