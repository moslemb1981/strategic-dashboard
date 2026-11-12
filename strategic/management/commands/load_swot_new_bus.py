"""ثبت SWOT و TOWS سه کسب‌وکار جدید (صافکاری و نقاشی، بعد از گارانتی (وارانتی)، صادرات).

    python manage.py load_swot_new_bus           # گزارش (بدون تغییر)
    python manage.py load_swot_new_bus --apply   # ثبت
    python manage.py load_swot_new_bus --apply --replace   # حذف SWOT/TOWS قبلی همان سه کسب‌وکار و ثبت دوباره

• کسب‌وکاری که از قبل SWOT یا TOWS دارد دست نمی‌خورد، مگر با --replace.
• کسب‌وکارهای قبلی (بسته خدمت، گارانتی، قطعات، آپشن، تعمیرات، واسطه‌گری) هیچ‌وقت تغییر نمی‌کنند.
• پیش از ثبت، پشتیبان JSON در backups/ ساخته می‌شود."""
import datetime
import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from strategic.models import BusinessUnit, SWOTItem, TOWSStrategy, PestelFactor, PorterForce
from ._swot_new_data import DATA


class Command(BaseCommand):
    help = "ثبت SWOT و TOWS سه کسب‌وکار جدید"

    def add_arguments(self, p):
        p.add_argument("--apply", action="store_true")
        p.add_argument("--replace", action="store_true")

    def handle(self, *a, **o):
        plan = []
        for key, d in DATA.items():
            bus = [b for b in BusinessUnit.objects.all() if key in b.name]
            if len(bus) != 1:
                self.stdout.write(self.style.WARNING(f"· «{key}»: {len(bus)} کسب‌وکار منطبق — رد شد"))
                continue
            bu = bus[0]
            n_sw = SWOTItem.objects.filter(business_unit=bu).count()
            n_to = TOWSStrategy.objects.filter(business_unit=bu).count()
            if (n_sw or n_to) and not o["replace"]:
                self.stdout.write(self.style.WARNING(f"· {bu.name}: از قبل {n_sw} مورد SWOT و {n_to} راهبرد TOWS دارد — رد شد (برای جایگزینی: --replace)"))
                continue
            for cat in "swot":
                ws = [x[2] for x in d[cat]]
                assert ws == sorted(ws, reverse=True), (key, cat)
            n_tows = sum(len(v) for v in d["tows"].values())
            self.stdout.write(f"■ {bu.name}: S={len(d['s'])} W={len(d['w'])} O={len(d['o'])} T={len(d['t'])} | TOWS={n_tows}"
                              + (f"  (حذف {n_sw} SWOT و {n_to} TOWS قبلی)" if (n_sw or n_to) else ""))
            plan.append((bu, d))
        if not o["apply"]:
            self.stdout.write(self.style.WARNING("حالت گزارش — برای ثبت: --apply"))
            return
        os.makedirs("backups", exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        bu_ids = [b.pk for b, _ in plan]
        snap = {
            "swot": list(SWOTItem.objects.filter(business_unit_id__in=bu_ids).values()),
            "tows": list(TOWSStrategy.objects.filter(business_unit_id__in=bu_ids).values()),
        }
        bpath = f"backups/swot_tows_before_{stamp}.json"
        with open(bpath, "w", encoding="utf-8") as fh:
            json.dump(snap, fh, ensure_ascii=False, default=str)
        with transaction.atomic():
            total_s = total_t = 0
            for bu, d in plan:
                SWOTItem.objects.filter(business_unit=bu).delete()
                TOWSStrategy.objects.filter(business_unit=bu).delete()
                objs = {}
                for cat in "swot":
                    for i, (title, expl, weight, pe, po) in enumerate(d[cat], start=1):
                        text = f"{title}: {expl}"[:300]
                        it = SWOTItem(category=cat, text=text, weight=weight, business_unit=bu,
                                      impact="high" if weight >= 4 else "med")
                        if pe:
                            it.source_pestel = PestelFactor.objects.filter(text__icontains=pe).first()
                        if po:
                            it.source_porter = PorterForce.objects.filter(text__icontains=po).first()
                        it.save()
                        objs[f"{cat.upper()}{i}"] = it
                        total_s += 1
                for cat, rows in d["tows"].items():
                    for order, (title, codes, expl) in enumerate(rows, start=1):
                        t = TOWSStrategy.objects.create(
                            category=cat, order=order, business_unit=bu,
                            text=f"{title} ({codes}):\nشرح: {expl}")
                        t.source_items.set([objs[c] for c in codes.split(",") if c in objs])
                        total_t += 1
        self.stdout.write(self.style.SUCCESS(f"{total_s} مورد SWOT و {total_t} راهبرد TOWS ثبت شد. پشتیبان: {bpath}"))
