"""ثبت بوم کسب‌وکار تدوین‌شده (تأییدشده) برای ۹ کسب‌وکار.

    python manage.py load_business_canvas           # گزارش (بدون تغییر)
    python manage.py load_business_canvas --apply   # ثبت

• هر کسب‌وکار که فقط «پیش‌نویس خودکار» دارد، ابتدا پیش‌نویس‌هایش حذف و بوم تدوین‌شده جایگزین می‌شود.
• کسب‌وکاری که مورد دستی/ویرایش‌شده شما را دارد دست نمی‌خورد (رد می‌شود).
• پیش از تغییر، پشتیبان JSON در backups/ ساخته می‌شود.
"""
import datetime
import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from strategic.models import BusinessUnit, BusinessCanvasItem
from ._canvas_curated import CURATED

AUTO = "[پیش‌نویس خودکار]"
MARK = "[بوم تدوین‌شده]"
NEW_KEYS = ("صافکاری", "وارانتی", "صادرات")  # فقط از داده کم دیتابیس؛ به‌صورت پیش‌نویس ثبت می‌شوند


class Command(BaseCommand):
    help = "ثبت بوم کسب‌وکار تدوین‌شده برای ۶ کسب‌وکار قبلی"

    def add_arguments(self, p):
        p.add_argument("--apply", action="store_true")
        p.add_argument("--only", default="", help="فقط این کسب‌وکارها (کلیدواژه‌ها با ویرگول) مثلاً: صافکاری,وارانتی,صادرات")
        p.add_argument("--force", action="store_true", help="جایگزینی بوم‌هایی که قبلاً با همین دستور ثبت شده‌اند (ویرایش‌های شما از بین می‌رود)")

    def handle(self, *a, **o):
        plan = []
        only = [x.strip() for x in o["only"].split(",") if x.strip()]
        for key, blocks in CURATED.items():
            if only and key not in only:
                continue
            bus = [b for b in BusinessUnit.objects.all() if key in b.name]
            if len(bus) != 1:
                self.stdout.write(self.style.WARNING(f"· «{key}»: {len(bus)} کسب‌وکار منطبق پیدا شد — رد شد"))
                continue
            bu = bus[0]
            existing = BusinessCanvasItem.objects.filter(business_unit=bu)
            if existing.filter(note__startswith=MARK).exists() and not (o["force"] or only):
                self.stdout.write(f"· {bu.name}: قبلاً ثبت شده — دست‌نخورده ماند")
                continue
            manual = existing.exclude(note__startswith=AUTO).exclude(note__startswith=MARK)
            if manual.exists():
                self.stdout.write(self.style.WARNING(f"· {bu.name}: {manual.count()} مورد دستی دارد — رد شد"))
                continue
            n = sum(len(v) for v in blocks.values())
            self.stdout.write(f"■ {bu.name}: {n} مورد  (حذف {existing.count()} مورد خودکار/قبلی)")
            for key_b, title in BusinessCanvasItem.BLOCK_CHOICES:
                self.stdout.write(f"   {title}: {len(blocks.get(key_b, []))}")
            plan.append((bu, blocks, key in NEW_KEYS))
        if not o["apply"]:
            self.stdout.write(self.style.WARNING("حالت گزارش — برای ثبت: --apply"))
            return
        os.makedirs("backups", exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bpath = f"backups/canvas_before_curated_{stamp}.json"
        with open(bpath, "w", encoding="utf-8") as fh:
            json.dump(list(BusinessCanvasItem.objects.values()), fh, ensure_ascii=False, default=str)
        with transaction.atomic():
            total = 0
            for bu, blocks, is_new in plan:
                BusinessCanvasItem.objects.filter(business_unit=bu).delete()
                for block, items in blocks.items():
                    for order, (text, src) in enumerate(items):
                        BusinessCanvasItem.objects.create(
                            business_unit=bu, block=block, text=text[:300], note=f"{MARK} منبع: {src}",
                            status="approved", order=order)
                        total += 1
        self.stdout.write(self.style.SUCCESS(f"{total} مورد ثبت شد. پشتیبان: {bpath}"))
