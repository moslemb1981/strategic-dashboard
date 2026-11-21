# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from strategic.models import CrossImpactFactor

# ترتیب و عنوان نهایی ۱۳ عامل ماتریس اثر متقابل، طبق درخواست مدیر.
# تطبیق بر اساس متن قدیمی انجام می‌شود (چون بعضی عنوان‌ها هم اصلاح شده‌اند).

ORDER = [
    ("نرخ ارز و تورم", "تغییرات نرخ ارز و تورم"),
    ("وضعیت بین‌المللی (سیاسی)", "ارتباطات بین‌المللی"),
    ("قدرت تأمین‌کنندگان", "قدرت تأمین‌کنندگان"),
    ("رفتار مشتریان", "رفتار مشتریان"),
    ("تأمین منابع مالی", "تأمین منابع مالی"),
    ("ثبات مدیریت", "ثبات مدیریت"),
    ("قطعات تقلبی", "قطعات غیراصلی"),
    ("قوانین و استانداردها", "قوانین و استانداردها"),
    ("نیروی انسانی توانمند", "نیروی انسانی توانمند"),
    ("ناترازی انرژی", "ناترازی منابع انرژی"),
    ("ناآرامی اجتماعی", "ناآرامی اجتماعی"),
    ("تغییرات فناوری", "تغییرات فناوری"),
    ("نرخ سرمایه‌گذاری", "نرخ سرمایه‌گذاری"),
]


class Command(BaseCommand):
    help = "ترتیب و عنوان ۱۳ عامل ماتریس اثر متقابل را طبق ترتیب نهایی درخواستی به‌روزرسانی می‌کند."

    def handle(self, *args, **options):
        updated, missing = 0, []
        for order, (old_text, new_text) in enumerate(ORDER, start=1):
            factor = CrossImpactFactor.objects.filter(text=old_text).first()
            if not factor:
                missing.append(old_text)
                continue
            factor.text = new_text
            factor.order = order
            factor.save(update_fields=["text", "order"])
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"{updated} عامل به‌روزرسانی شد."))
        if missing:
            self.stdout.write(self.style.WARNING("این عنوان‌های قدیمی پیدا نشدند: " + " | ".join(missing)))
