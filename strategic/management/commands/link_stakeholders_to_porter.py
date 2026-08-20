# -*- coding: utf-8 -*-
"""اتصال ذینفعان به آیتم‌های Porter واقعاً مرتبط — طبق ماهیت این ارتباط
(دسته‌بندی/مفهومی، نه تطبیق کلمه‌ای)، فقط ذینفعانی که ماهیتاً «بیرونی/بازاری»
هستن (تامین‌کننده، مشتری/شبکه، خودروساز) به دسته‌ی متناظرشون از ۵ نیروی Porter
وصل شدن. ذینفعان داخلی/سازمانی (مدیریت آموزش، کیفیت، پرسنل و...) عمداً بدون
اتصال موندن، چون ۵ نیروی Porter ذاتاً درباره‌ی رقابت و بازار بیرونیه."""
from django.core.management.base import BaseCommand
from strategic.models import Stakeholder, PorterForce


# (نام دقیق ذینفع، [شناسه‌های آیتم Porter مرتبط])
NAME_TO_PORTER_PKS = {
    "تامین کنندگان قطعه آپشن": [15, 16, 17],
    "تامین کنندگان": [15, 16, 17],
    "تامین کنندگان قطعات": [15, 16, 17],
    "معاونت تامین": [15, 16, 17],
    "معاونت های تامین / لجستیک": [15, 16, 17],

    "شبکه نمایندگیها": [13, 14, 10],
    "شبکه نمایندگیها/ تعمیرگاه مرکزی": [13, 14, 10],
    "نمایندگان مجاز شبکه": [13, 14],
    "مدیریت امور مشتریان": [8, 10],

    "مشتریان": [6, 7, 9, 10, 11, 12],

    "شرکت سایپا": [23],
    "خودروساز (کیفیت)": [23],
    "خودرو سازان\n(سایپا / پارس خودرو / زامیاد )": [23],
    "شرکت پارس خودرو": [23],
    "شرکت زامیاد": [23],
}


class Command(BaseCommand):
    help = "ذینفعان بیرونی/بازاری را به آیتم‌های واقعاً مرتبط ۵ نیروی Porter وصل می‌کند."

    def handle(self, *args, **options):
        porter_by_pk = {p.pk: p for p in PorterForce.objects.all()}
        linked, not_found = 0, []
        for name, porter_pks in NAME_TO_PORTER_PKS.items():
            stakeholders = Stakeholder.objects.filter(name=name)
            if not stakeholders.exists():
                not_found.append(f"ذینفع «{name}» یافت نشد")
                continue
            for sh in stakeholders:
                for ppk in porter_pks:
                    porter = porter_by_pk.get(ppk)
                    if not porter:
                        continue
                    sh.related_porters.add(porter)
                    linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط ذینفع-Porter."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
