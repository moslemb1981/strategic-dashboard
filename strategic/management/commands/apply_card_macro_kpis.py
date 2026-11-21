"""اتصال شاخص‌های کلان (I1..I25) به کارت‌های نقشه استراتژیک طبق فهرست پیشنهادی.

  python manage.py apply_card_macro_kpis            # فقط گزارش (چیزی ذخیره نمی‌شود)
  python manage.py apply_card_macro_kpis --apply    # اعمال

فقط اتصال اضافه می‌کند (وزن ۱۰۰) و یک اتصال اشتباه شناخته‌شده را برمی‌دارد
(I16 از کارت «تأمین بر اساس MRP» بازرگانی قطعات). اتصال‌های موجود دیگر دست نمی‌خورند.
"""
from django.core.management.base import BaseCommand

from strategic.models import CompanyKPI, ObjectiveKPIWeight, StrategicObjective

# نام (بخشی از نام) کسب‌وکار ← شماره
BU_KEY = {1: "بسته خدمت", 2: "گارانتی", 3: "بازرگانی قطعات", 4: "آپشن", 5: "خدمات تعمیراتی", 6: "واسطه"}

ADD = {
    "I1": [(1, "F1"), (2, "F1"), (4, "F1"), (5, "F1")],
    "I2": [(3, "F3")], "I3": [(3, "F3"), (3, "P19")], "I4": [(3, "P5"), (5, "P4")],
    "I5": [(4, "F3"), (4, "F6")], "I6": [(4, "F3"), (4, "C5")], "I7": [(1, "F3")],
    "I9": [(5, "F4"), (5, "F3")],
    "I10": [(5, "C1"), (2, "C3")], "I11": [(5, "C1"), (5, "C3")], "I12": [(5, "C1")], "I13": [(5, "C1")],
    "I14": [(2, "P14"), (1, "P10")], "I15": [(2, "P6"), (2, "P9"), (5, "C1")],
    "I16": [(2, "P2"), (2, "F4")], "I17": [(5, "F6"), (5, "P4")],
    "I18": [(2, "P9"), (5, "P9")], "I19": [(2, "P9"), (5, "P9")],
    "I20": [(5, "P3"), (5, "P4")],
    "I21": [(2, "L1"), (3, "L1"), (4, "L1"), (5, "L1"), (5, "L7")],
    "I22": [(2, "L1"), (3, "L1"), (4, "L1"), (5, "L1"), (5, "L2")],
    "I23": [(6, "F3"), (6, "F1")], "I24": [(5, "P2"), (5, "F2")], "I25": [(2, "P3"), (3, "F2")],
}
REMOVE = [("I16", 3, "P5")]


def find_obj(bu, code):
    return StrategicObjective.objects.filter(business_unit__name__contains=BU_KEY[bu], code=code).first()


class Command(BaseCommand):
    help = "اتصال شاخص‌های کلان به کارت‌های نقشه طبق فهرست پیشنهادی (پیش‌فرض: فقط گزارش)"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **opts):
        apply_ = opts["apply"]
        kpis = {k.code: k for k in CompanyKPI.objects.all()}
        added = skipped = missing = removed = 0
        for code, items in ADD.items():
            kpi = kpis.get(code)
            if not kpi:
                self.stdout.write(f"شاخص {code} پیدا نشد"); missing += len(items); continue
            for bu, ocode in items:
                obj = find_obj(bu, ocode)
                if not obj:
                    self.stdout.write(f"کارت پیدا نشد: کسب‌وکار {bu} / {ocode}"); missing += 1; continue
                if ObjectiveKPIWeight.objects.filter(objective=obj, kpi=kpi).exists():
                    skipped += 1; continue
                added += 1
                if apply_:
                    ObjectiveKPIWeight.objects.create(objective=obj, kpi=kpi, weight=100)
        for code, bu, ocode in REMOVE:
            obj, kpi = find_obj(bu, ocode), kpis.get(code)
            if obj and kpi:
                qs = ObjectiveKPIWeight.objects.filter(objective=obj, kpi=kpi)
                if qs.exists():
                    removed += qs.count()
                    if apply_:
                        qs.delete()
        self.stdout.write(f"اتصال جدید: {added} | از قبل موجود: {skipped} | پیدا نشد: {missing} | حذف‌شده: {removed}")
        self.stdout.write("اعمال شد." if apply_ else "فقط گزارش (برای اعمال --apply بزنید).")
