# -*- coding: utf-8 -*-
"""اتصال پروژه‌های تحول به اهداف استراتژیک واقعاً مرتبط — بر اساس تحلیل محتوایی
کارشناسی (عنوان پروژه در برابر عنوان هدف، با امتیازدهی وزنی بر اساس نایاب‌بودن
کلمات مشترک؛ کلمات عمومی مثل «افزایش»، «کاهش»، «فرآیند» حذف شدند). چندتا تطابق
با امتیاز بالا ولی موضوعاً بی‌ربط (تشخیص دستی، مثل «پیش‌بینی نیازهای مشتریان»
که فقط با «پیش‌بینی بودجه‌ی پیمانکاران» بر سر یک کلمه جفت شده بود) کنار گذاشته شدند.

نتیجه: ۳۷ ارتباط، برای ۳۱ هدف از ۱۷۸ — عمداً نه همه، فقط جاهایی که واقعاً
تطابق محتوایی روشن و قابل‌دفاع بود."""
from django.core.management.base import BaseCommand
from strategic.models import StrategicObjective, Initiative


# (شناسه‌ی هدف استراتژیک، کد پروژه)
PAIRS = [
    (33, '100EX003'), (33, '100EX004'), (65, '100EX011'), (108, 'T121P0148B01'),
    (108, '100PKK07071'), (175, '100EX144'), (81, 'T121P035A01'), (81, '100EX001'),
    (129, '100PKK07071'), (2, '100EX067'), (34, '100EX067'), (68, '100EX067'),
    (112, '100EX067'), (144, '100EX067'), (174, 'T121P018F01'), (176, '100EX011'),
    (91, '100EX139'), (91, 'T121P001A01'), (57, '100EX011'), (145, '100EX033'),
    (145, '100EX020'), (61, '100EX075'), (48, '100EX070'), (48, '100EX115'),
    (77, '100PKK07071'), (121, '100PKK07071'), (154, '100EX119'), (84, '100EX117'),
    (5, '100EX137'), (37, '100EX137'), (71, '100EX119'), (115, '100EX119'),
    (79, '100EX120'), (148, '100EX137'), (7, '100EX119'), (117, '100PKK07071'),
    (150, '100EX119'),
]


class Command(BaseCommand):
    help = "پروژه‌های تحول را به اهداف استراتژیک واقعاً مرتبط (بر اساس تحلیل کارشناسی) وصل می‌کند."

    def handle(self, *args, **options):
        init_by_code = {i.code: i for i in Initiative.objects.all()}
        linked, not_found = 0, []
        for obj_pk, code in PAIRS:
            try:
                obj = StrategicObjective.objects.get(pk=obj_pk)
            except StrategicObjective.DoesNotExist:
                not_found.append(f"هدف {obj_pk} یافت نشد")
                continue
            init = init_by_code.get(code)
            if not init:
                not_found.append(f"پروژه با کد {code} یافت نشد")
                continue
            init.objectives.add(obj)
            linked += 1

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} ارتباط هدف-پروژه."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
