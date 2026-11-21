# -*- coding: utf-8 -*-
"""اتصال ریسک‌های سازمانی به پروژه‌های تحول واقعاً مرتبط — بر اساس تطبیق مستقیم با
متن «اقدام کاهش» خودِ هر ریسک.

⚠️ نسخه‌ی دوم و اصلاح‌شده: نسخه‌ی اول (بند قبلی) به‌خاطر تفاوت کاراکتر عربی «ي»
در برابر فارسی «ی» توی عناوین پروژه‌ها، چندین مورد رو جا انداخته بود، و یه مورد
هم اشتباه به ریسک نادرست وصل شده بود (Disaster Recovery به ریسک «آلودگی محیط
زیست» به‌جای ریسک «ناامنی منطقه»). این نسخه با جست‌وجوی نرمال‌شده (بدون حساسیت
به ي/ی) دوباره از صفر بررسی و تصحیح شد — بر اساس دفتر ثبت ریسک واقعی کاربر."""
from django.core.management.base import BaseCommand
from strategic.models import Risk, Initiative


# (شناسه‌ی ریسک، [کدهای پروژه‌ی مرتبط از متن «اقدام کاهش» خودِ همون ریسک])
# شماره‌ی ردیف در صفحه‌ی «نقشه ریسک» کاربر هم جلوی هرکدوم نوشته شده
LINKS = [
    (25, ["100PKK05051", "100PSH04037", "100PKK05052", "100EX052", "100PSH03021"]),
    # #۱ ناامنی منطقه و شرایط جنگی

    (24, ["100PSH08055", "100PSH08049", "T121P099A01"]),
    # #۲ معرفی محصولات جدید با تیراژ پایین

    (21, ["100PME15016", "T121P0106B01", "T121P024B01", "100PME02001"]),
    # #۳ افزایش مطالبات معوق

    (19, ["100PSH04004", "100PSH04037", "100PSH08049", "100PSH08055"]),
    # #۴ کاهش کیفیت محصولات گروه

    (23, ["100PKA06058"]),
    # #۵ خروج بالای نیروی انسانی ماهر از شبکه

    (20, ["100PKA03002"]),
    # #۶ عدم تأمین مناسب شرکت‌های گروه

    (27, ["T121P0114B01", "100PSH06017", "T121P0116B01", "T121P0115B01"]),
    # #۷ آلودگی محیط زیست — توجه: Disaster Recovery اشتباهاً اینجا بود، حذف شد

    (26, ["T121P039A01"]),
    # #۸ تشدید تحریم‌های اقتصادی کشور

    (22, ["100PSH13056", "100PKK07006", "100PKK03031"]),
    # #۹ توزیع مستقیم قطعات توسط شرکت‌های گروه
]

# اتصال اشتباهی که باید حذف بشه: Disaster Recovery به ریسک «آلودگی محیط زیست» (۲۷)
WRONG_LINKS = [
    (27, "100PSH03021"),
]


class Command(BaseCommand):
    help = "ریسک‌ها را به پروژه‌های تحول واقعاً مرتبط وصل می‌کند (نسخه‌ی اصلاح‌شده و کامل)."

    def handle(self, *args, **options):
        init_by_code = {i.code: i for i in Initiative.objects.all()}

        removed = 0
        for risk_pk, code in WRONG_LINKS:
            try:
                risk = Risk.objects.get(pk=risk_pk)
                init = init_by_code.get(code)
                if init and init in risk.initiatives.all():
                    risk.initiatives.remove(init)
                    removed += 1
            except Risk.DoesNotExist:
                pass

        linked, not_found = 0, []
        for risk_pk, codes in LINKS:
            try:
                risk = Risk.objects.get(pk=risk_pk)
            except Risk.DoesNotExist:
                not_found.append(f"ریسک {risk_pk} یافت نشد")
                continue
            for code in codes:
                init = init_by_code.get(code)
                if not init:
                    not_found.append(f"پروژه با کد {code} یافت نشد")
                    continue
                if init not in risk.initiatives.all():
                    risk.initiatives.add(init)
                    linked += 1

        self.stdout.write(self.style.SUCCESS(f"اتصال اشتباه حذف شد: {removed} مورد."))
        self.stdout.write(self.style.SUCCESS(f"ارتباط جدید ثبت شد: {linked} مورد."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)

