# -*- coding: utf-8 -*-
"""پاک‌سازی ارتباطات اشتباه «پروژه ↔ هدف استراتژیک» که به‌خاطر یه باگ توی چندتا
اسکریپت قدیمی (link_option/parts_trading/service_package_objectives_to_initiatives)
ایجاد شده بودن — اون اسکریپت‌ها موقع جست‌وجوی پروژه بر اساس کد، کسب‌وکار پروژه رو
چک نمی‌کردن، فقط کد رو (که ممکنه بین کسب‌وکارها یکتا نباشه).

طبق قانون اصلی سامانه (مطابق مستندات اولیه): هر پروژه فقط باید به اهداف
استراتژیک همون کسب‌وکار خودش وصل باشه.

این اسکریپت فقط و فقط رابطه‌ی «objectives» (اهداف استراتژیک مرتبط) رو دست‌کاری
می‌کنه — با حذف نقطه‌ای (remove) فقط همون ارتباط‌های اشتباه، نه با پاک‌کردن کل
رابطه. به هیچ رابطه‌ی دیگه‌ای (شاخص‌های مبنا، شاخص‌های عملیاتی، TOWS، ریسک، و
هیچ فیلد دیگه‌ای از پروژه) دست نمی‌زنه.

نحوه‌ی اجرا (فقط یک‌بار):
    python manage.py cleanup_wrong_bu_objectives
"""
from django.core.management.base import BaseCommand
from strategic.models import Initiative


class Command(BaseCommand):
    help = "حذف ارتباطات اشتباه اهداف استراتژیک که کسب‌وکارشون با کسب‌وکار پروژه یکی نیست."

    def handle(self, *args, **options):
        removed, affected_initiatives = 0, 0
        for init in Initiative.objects.all().prefetch_related("objectives"):
            wrong_objs = [o for o in init.objectives.all() if o.business_unit_id != init.business_unit_id]
            if not wrong_objs:
                continue
            for obj in wrong_objs:
                init.objectives.remove(obj)
                removed += 1
            affected_initiatives += 1

        self.stdout.write(self.style.SUCCESS(
            f"{removed} ارتباط اشتباه از {affected_initiatives} پروژه حذف شد."
        ))
