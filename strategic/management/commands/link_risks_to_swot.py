# -*- coding: utf-8 -*-
"""
اتصال ریسک‌های سطح کلان شرکت به موارد «تهدید»/«ضعف» SWOT مرتبط، بر اساس تحلیل محتوایی
(نه شماره‌ی ردیف). فقط مواردی که از نظر موضوع کاملاً روشن بودن وصل شدن — نه هر ۹ ریسک
لزوماً به چیزی وصل می‌شه (اگه هیچ مورد SWOT با موضوع مشابه پیدا نشد، همون ریسک بدون
ارتباط می‌مونه، بدون خطا).

بعد از اتصال، بج «ریشه» (ردیابی خودکار) خودش زنجیره را تا PESTEL/Porter/ذینفع دنبال
می‌کند — نیازی به کار دستی بیشتر نیست.

⚠️ طبق توافق با کاربر: این ارتباط‌ها تحلیل اولیه‌ی هوش مصنوعی هستند و باید توسط کاربر
بازبینی و در صورت نیاز اصلاح شوند.
"""
from django.core.management.base import BaseCommand
from strategic.models import Risk, SWOTItem


def _norm(s):
    return (s or "").replace("\u200c", "").replace(" ", "").strip()


# (بخشی از عنوان ریسک، [لیستی از بخش‌هایی از متن SWOT که باید بهش وصل بشه])
RISK_TO_SWOT = [
    ("تشدید تحریم‌های اقتصادی", [
        "تحریم‌های بین‌المللی: ممانعت از ورود قطعات",
        "تشدید تحریم‌های بین‌المللی و دشواری تامین قطعات فنی خاص",
    ]),
    ("ناامنی منطقه و شرایط جنگ‌آلود", [
        "افزایش تعطیلی شرکتها به علت وقوع جنگ",
        "افزایش تعطیلی شرکت‌ها به علت وقوع جنگ",
        "تولید بسیار محدود صنایع پتروشیمی و فولادی به دلیل آسیب های جنگ",
        "تولید بسیار محدود صنایع پتروشیمی و فولادی به‌دلیل آسیب‌های جنگ",
        "تغییر اولویت مشتری ناشی از جنگ",
    ]),
    ("آلودگی محیط زیست ناشی از نشت مواد شیمیایی", [
        "افزایش آلودگی آبخوان و مخاطرات زیست محیطی",
        "افزایش الزامات و حساسیت زیست‌محیطی نسبت به دفع نامناسب قطعات",
        "افزایش آلودگی زیست‌محیطی ناشی از پسماند",
    ]),
    ("خروج بالای نیروی انسانی ماهر از شبکه", [
        "خروج سرمایه انسانی متخصص (کارشناسان فنی و عیب‌یابی)",
        "خروج سرمایه های انسانی",
        "خروج نیروی انسانی متخصص فنی از سازمان و شبکه تعمیرگاهی",
    ]),
]


class Command(BaseCommand):
    help = "ریسک‌های کلان شرکت را بر اساس تحلیل محتوایی به موارد تهدید/ضعف SWOT مرتبط وصل می‌کند."

    def handle(self, *args, **options):
        swot_items = list(SWOTItem.objects.filter(category__in=["t", "w"]))
        linked, not_found = 0, []

        for title_key, swot_texts in RISK_TO_SWOT:
            risk = Risk.objects.filter(title__icontains=title_key).first()
            if not risk:
                not_found.append(f"ریسک یافت نشد: {title_key}")
                continue
            for swot_text in swot_texts:
                match = None
                for si in swot_items:
                    if _norm(swot_text) in _norm(si.text):
                        match = si
                        break
                if not match:
                    not_found.append(f"مورد SWOT یافت نشد برای «{title_key}»: {swot_text}")
                    continue
                if not risk.related_swot_items.filter(pk=match.pk).exists():
                    risk.related_swot_items.add(match)
                    linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط ریسک←SWOT."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده (رد شدند، بدون خطا):"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
