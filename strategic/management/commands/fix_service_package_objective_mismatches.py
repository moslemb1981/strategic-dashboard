# -*- coding: utf-8 -*-
"""اصلاح محتوایی ۵ هدف «بسته خدمت» که بعد از بررسی دقیق عنوان‌ها، پروژه‌های
اشتباه (موضوعاً بی‌ربط) بهشون وصل شده بودن (بند ۲۰۶). این دستور جایگزین بند
۲۰۶ نمی‌شه، بلکه روش اصلاحیه:

۱) C1 (قیمت مناسب) و P7 (روابط با مشتری) — همه‌ی پروژه‌هاشون (که واقعاً
   درباره‌ی «تأمین قطعه» بودن، نه قیمت یا رابطه با مشتری) حذف و به P3 (خلق
   شبکه‌ای از تأمین‌کنندگان خدمت — که دقیقاً معنایی‌شون بود و خالی مونده بود)
   منتقل می‌شن.
۲) P1 (بسته‌های خدمت متنوع)، P2 (کیفیت توافق‌شده با تأمین‌کنندگان)، P13 (اخذ
   مجوز قانونی) — پروژه‌های اشتباهشون (که موضوعاً کاملاً بی‌ربط بودن: املاک/
   مالی برای P1، وصول مطالبات برای P2، شکایات مشتری برای P13) حذف می‌شن و
   خالی می‌مونن، چون هیچ‌کدوم از ۹۰ پروژه‌ی موجود واقعاً به این ۳ هدف مرتبط
   نبود."""
from django.core.management.base import BaseCommand
from strategic.models import StrategicObjective, Initiative, BusinessUnit


# کدهایی که باید از C1 و P7 حذف و به P3 منتقل بشن
SUPPLY_CODES = [
    'T121P0129A01', 'T121P044A01', 'T121P047B01', 'T121P078A01', '100EX131',
    '100EX008', '100EX137', '100EX138', '100PKK01011',
    'T121P079B01', 'T121P081B01-01', '100EX108',
]

# اهدافی که باید کاملاً خالی بشن (پروژه‌هاشون موضوعاً بی‌ربط بودن)
CLEAR_COMPLETELY = ['P1', 'P2', 'P13']


class Command(BaseCommand):
    help = "اصلاح محتوایی C1/P7/P1/P2/P13 در نقشه‌ی استراتژیک بسته خدمت."

    def handle(self, *args, **options):
        bu = BusinessUnit.objects.filter(name__icontains="بسته خدمت").first()
        obj_by_code = {o.code: o for o in StrategicObjective.objects.filter(business_unit=bu)}
        init_by_code = {i.code: i for i in Initiative.objects.all() if i.code}

        removed, added = 0, 0

        # ۱) پاک‌کردن کامل C1 و P7
        for code in ['C1', 'P7']:
            obj = obj_by_code[code]
            count = obj.initiatives.count()
            obj.initiatives.clear()
            removed += count
            self.stdout.write(f"  {code}: {count} پروژه حذف شد (پاک‌سازی کامل)")

        # ۲) وصل‌کردن پروژه‌های تأمین به P3
        p3 = obj_by_code['P3']
        for code in SUPPLY_CODES:
            init = init_by_code.get(code)
            if init:
                init.objectives.add(p3)
                added += 1
        self.stdout.write(f"  P3: {added} پروژه اضافه شد")

        # ۳) پاک‌سازی کامل P1، P2، P13
        for code in CLEAR_COMPLETELY:
            obj = obj_by_code[code]
            count = obj.initiatives.count()
            obj.initiatives.clear()
            removed += count
            self.stdout.write(f"  {code}: {count} پروژه حذف شد (پاک‌سازی کامل)")

        self.stdout.write(self.style.SUCCESS(f"\nجمع کل: {removed} ارتباط حذف، {added} ارتباط جدید اضافه شد."))
