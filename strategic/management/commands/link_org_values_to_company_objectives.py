# -*- coding: utf-8 -*-
"""بازسازی کامل اتصال ۸ ارزش سازمانی به اهداف کلان — نسخه‌ی معماری اصلاح‌شده.
جایگزین نسخه‌ی قبلی (که ارزش‌ها رو به اهداف نقشه‌ی استراتژیک، ۱۷۸ تایی و
مخصوص هر کسب‌وکار، وصل می‌کرد) — چون از نظر منطقی، ارزش‌های کل‌شرکتی باید
به اهداف کلان کل‌شرکتی (نه هدف مخصوص یه کسب‌وکار خاص) وصل بشن؛ دقیقاً همون
سطحی که خودِ اهداف کلان هم به هدف گروه سایپا وصلن.

تطبیق بر پایه‌ی محتوای دقیق هر هدف کلان (نه فقط عنوان کلی) انجام شده."""
from django.core.management.base import BaseCommand
from strategic.models import OrgValue, CompanyObjective


# (متن ارزش، [کدهای هدف کلان مرتبط])
VALUE_TO_OBJECTIVES = {
    "رقابت سالم": ["O4"],
    "شفافیت و اعتمادآفرینی": ["O5"],
    "کرامت انسانی ناظر بر حقوق ذی‌نفعان": ["O15", "O16"],
    "اطلاع‌رسانی جامع به ذی‌نفعان": ["O14", "O13"],
    "توان‌افزایی و توسعه قابلیت‌های کارکنان": ["O11", "O15"],
    "نوآوری بازار محور": ["O6", "O8"],
    "وحدت و کارتیمی": ["O12"],
    "مشتری‌مداری": ["O1", "O2", "O3", "O7", "O9", "O10", "O13"],
}


class Command(BaseCommand):
    help = "ارزش‌های سازمانی را به اهداف کلان واقعاً مرتبط وصل می‌کند (معماری اصلاح‌شده)."

    def handle(self, *args, **options):
        obj_by_code = {o.code: o for o in CompanyObjective.objects.all()}
        total = 0
        not_found = []

        for value_text, codes in VALUE_TO_OBJECTIVES.items():
            try:
                value = OrgValue.objects.get(text=value_text)
            except OrgValue.DoesNotExist:
                not_found.append(f"ارزش «{value_text}» یافت نشد")
                continue
            objs = [obj_by_code[c] for c in codes if c in obj_by_code]
            missing = [c for c in codes if c not in obj_by_code]
            if missing:
                not_found.append(f"کد(های) {missing} برای ارزش «{value_text}» یافت نشد")
            value.related_objectives.set(objs)
            total += len(objs)
            self.stdout.write(f"  {value_text}: {len(objs)} هدف کلان")

        self.stdout.write(self.style.SUCCESS(f"\nجمع کل: {total} ارتباط ارزش-هدف کلان ثبت شد."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
