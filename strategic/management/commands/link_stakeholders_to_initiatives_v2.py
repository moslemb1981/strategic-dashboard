# -*- coding: utf-8 -*-
"""اتصال ذینفعان به پروژه‌های تحول واقعاً مرتبط — دور دوم، تکمیل‌کننده‌ی بند ۱۸۹.
این‌بار با نرمال‌سازی کاراکتر عربی/فارسی (ي↔ی) که توی جست‌وجوی ریسک‌ها هم کمک
کرده بود. از ۵۴ تطابق پیشنهادی اولیه، بعد از بررسی دستی کیفیت، فقط ۱۶ مورد
واقعاً قوی و موضوعاً درست نگه داشته شد؛ بقیه (که فقط روی کلمات عمومی مثل «موقع»
یا «اعمال» یا اسم شرکت به‌تنهایی جفت شده بودن) کنار گذاشته شدن."""
from django.core.management.base import BaseCommand
from strategic.models import Stakeholder, Initiative


# (شناسه‌ی ذینفع، کد پروژه)
PAIRS = [
    (391, "T121P098A01"), (445, "T121P098A01"),
    (393, "100EX053"),
    (460, "100EX039"), (461, "100EX039"), (462, "100EX039"),
    (455, "100EX052"), (456, "100EX052"), (457, "100EX052"), (458, "100EX052"), (459, "100EX052"),
    (398, "T121P076A01"), (405, "T121P076A01"),
    (550, "T121P040C01"),
    (557, "100EX060"),
    (567, "100EX004"),
]


class Command(BaseCommand):
    help = "دور دوم اتصال ذینفعان به پروژه‌های تحول واقعاً مرتبط (بند ۱۸۹ تکمیلی)."

    def handle(self, *args, **options):
        init_by_code = {i.code: i for i in Initiative.objects.all()}
        linked, not_found = 0, []
        for sh_pk, code in PAIRS:
            try:
                sh = Stakeholder.objects.get(pk=sh_pk)
            except Stakeholder.DoesNotExist:
                not_found.append(f"ذینفع {sh_pk} یافت نشد")
                continue
            init = init_by_code.get(code)
            if not init:
                not_found.append(f"پروژه با کد {code} یافت نشد")
                continue
            sh.related_initiatives.add(init)
            linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط ذینفع-پروژه."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
