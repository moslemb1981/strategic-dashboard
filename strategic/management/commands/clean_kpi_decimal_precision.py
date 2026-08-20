# -*- coding: utf-8 -*-
"""اصلاح دقت اعشار مقادیر عددی (هدف/عملکرد/درصد تحقق) در بانک شاخص‌های عملیاتی و
شاخص‌های کلیدی شرکت — طبق گزارش کاربر، بعضی مقادیر عدد اعشاری خیلی طولانی (مثلاً
58.139534883720934) داشتن که احتمالاً حاصل یه محاسبه‌ی خودکار (تقسیم) بدون گرد
کردن بوده. این دستور فقط رشته‌های عددی رو گرد می‌کنه؛ هر مقداری که عدد نباشه
(مثل «—» یا یادداشت متنی) دست‌نخورده می‌مونه."""
from django.core.management.base import BaseCommand
from strategic.models import OperationalKPI, CompanyKPI
from strategic.forms import clean_number_string


FIELDS = ["target_1404", "actual_1404", "target_1405", "actual_1405", "progress_1405"]


class Command(BaseCommand):
    help = "دقت اعشار مقادیر عددی شاخص‌های عملیاتی و کلان را به حداکثر ۲ رقم گرد می‌کند."

    def handle(self, *args, **options):
        total_changed = 0
        for model, label in [(OperationalKPI, "شاخص عملیاتی"), (CompanyKPI, "شاخص کلان")]:
            changed_this_model = 0
            for obj in model.objects.all():
                dirty = False
                for field in FIELDS:
                    old_val = getattr(obj, field)
                    new_val = clean_number_string(old_val)
                    if new_val != old_val:
                        setattr(obj, field, new_val)
                        dirty = True
                if dirty:
                    obj.save(update_fields=FIELDS)
                    changed_this_model += 1
            self.stdout.write(self.style.SUCCESS(f"{label}: {changed_this_model} رکورد اصلاح شد."))
            total_changed += changed_this_model

        self.stdout.write(self.style.SUCCESS(f"جمع کل: {total_changed} رکورد اصلاح شد."))
