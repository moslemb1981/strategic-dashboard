# -*- coding: utf-8 -*-
"""پاک‌سازی رکوردهای مزاحمی که به‌خاطر یک باگ در «ورود از اکسل» بانک شاخص‌های
عملیاتی ساخته شدن (بند ۳۰۲/۳۰۳ در DEPLOY.md).

**علت باگ**: تابع ورود از اکسل به‌جای انتخاب صریح شیت اول («شاخص‌های عملیاتی»)،
از wb.active استفاده می‌کرد — که به شیتی وابسته است که هنگام «آخرین ذخیره در
اکسل» باز/انتخاب بوده. اگر کاربر روی تب «اطلاعات روند شاخص‌ها» کلیک کرده و بعد
فایل را ذخیره کرده بود، سامانه به‌جای شیت اول، داده‌ی شیت روند را می‌خواند و هر
ردیف آن را به‌اشتباه به‌عنوان یک شاخص عملیاتی جدید می‌ساخت — با «کد» برابر شماره‌ی
ردیف (۱، ۲، ۳...)، «عنوان» برابر کد واقعی شاخص، «حوزه» = Q، و «واحد» = سال.

این دستور، شاخص‌های عملیاتی‌ای که **کدشان کاملاً عددی** است (مثل «10»، «100») را
پیدا می‌کند — چون در این سامانه هیچ کد واقعی شاخصی صرفاً عدد نیست (همه با پیشوند
حرفی مثل CRM-09-00، HR-78-03، PP-01-03 و... هستند)، این یک نشانه‌ی مطمئن است که
آن رکورد محصول همین باگ بوده، نه یک شاخص واقعی.

**پیش‌فرض این دستور فقط نمایش (dry-run) است — چیزی پاک نمی‌شود.** بعد از دیدن
فهرست و اطمینان از درست بودنش، با پرچم --apply واقعاً حذف انجام می‌شود.

نحوه‌ی اجرا:
    python manage.py cleanup_bad_trend_import            # فقط نمایش فهرست (امن)
    python manage.py cleanup_bad_trend_import --apply     # حذف واقعی
"""
import re

from django.core.management.base import BaseCommand
from strategic.models import OperationalKPI

NUMERIC_CODE_RE = re.compile(r"^\d+$")


class Command(BaseCommand):
    help = "شاخص‌های عملیاتیِ ساخته‌شده توسط باگ «ورود اشتباه شیت روند» را پیدا/حذف می‌کند."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply", action="store_true",
            help="بدون این پرچم فقط فهرست نمایش داده می‌شود؛ با این پرچم واقعاً حذف می‌شود.",
        )

    def handle(self, *args, **options):
        apply_delete = options["apply"]

        suspects = [k for k in OperationalKPI.objects.all() if NUMERIC_CODE_RE.match(k.code or "")]

        if not suspects:
            self.stdout.write(self.style.SUCCESS("هیچ رکورد مشکوکی (کد کاملاً عددی) پیدا نشد."))
            return

        self.stdout.write(f"{len(suspects)} رکورد با کد کاملاً عددی پیدا شد:\n")
        for k in suspects:
            self.stdout.write(
                f"  - id={k.pk} | کد={k.code!r} | عنوان={k.title!r} | حوزه={k.domain} | واحد={k.unit!r}"
            )

        if not apply_delete:
            self.stdout.write(self.style.WARNING(
                "\nهیچ‌چیز حذف نشد (حالت نمایشی/dry-run). اگر فهرست بالا درست به‌نظر می‌رسد "
                "(همه‌شون کد عددی صِرف دارن و شاخص واقعی شما نیستن)، همین دستور رو با "
                "--apply دوباره اجرا کنید تا واقعاً حذف بشن:\n"
                "    python manage.py cleanup_bad_trend_import --apply"
            ))
            return

        count = len(suspects)
        for k in suspects:
            k.delete()

        self.stdout.write(self.style.SUCCESS(f"\n{count} رکورد مزاحم حذف شد."))
