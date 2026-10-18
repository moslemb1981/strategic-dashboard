"""گزارش CSV مقایسه‌ی درصد کارت‌ها: روش قدیمی (عملیاتی قدیمی) در برابر روش جدید (شاخص پشتیبان).

  python manage.py card_status_preview --out card_status_preview.csv
"""
import csv

from django.core.management.base import BaseCommand

from strategic import views as V
from strategic.models import ObjectiveKPIWeight, ObjectiveOperationalKPIWeight, StrategicObjective


class Command(BaseCommand):
    help = "پیش‌نمایش تغییر درصد کارت‌ها بین روش قدیمی و جدید"

    def add_arguments(self, parser):
        parser.add_argument("--out", default="card_status_preview.csv")

    def handle(self, *args, **opts):
        kw = {(w.objective_id, w.kpi_id): w.weight for w in ObjectiveKPIWeight.objects.all()}
        ow = {(w.objective_id, w.kpi_id): w.weight for w in ObjectiveOperationalKPIWeight.objects.all()}
        objs = list(StrategicObjective.objects.select_related("business_unit").prefetch_related(
            "linked_kpis", "linked_operational_kpis", "functional_strategies__linked_operational_kpis"))
        saved = V.CARD_STATUS_USE_SUPPORT_KPIS
        rows, changed, lost, gained = [], 0, 0, 0
        try:
            for o in objs:
                V.CARD_STATUS_USE_SUPPORT_KPIS = False
                old = V._objective_weighted_pct_status(o, kw, ow)[0]
                V.CARD_STATUS_USE_SUPPORT_KPIS = True
                new = V._objective_weighted_pct_status(o, kw, ow)[0]
                sup = len(V._objective_support_kpis(o))
                if old != new:
                    changed += 1
                    lost += new is None and old is not None
                    gained += old is None and new is not None
                rows.append((o.business_unit.name if o.business_unit else "", o.code, o.title,
                             "" if old is None else old, "" if new is None else new, sup,
                             "تغییر کرد" if old != new else ""))
        finally:
            V.CARD_STATUS_USE_SUPPORT_KPIS = saved
        with open(opts["out"], "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["کسب‌وکار", "کد", "عنوان کارت", "درصد قبلی", "درصد جدید", "تعداد شاخص پشتیبان", "وضعیت"])
            w.writerows(rows)
        self.stdout.write(f"کارت‌ها: {len(objs)} | تغییر کرده: {changed} | وضعیتش خالی می‌شود: {lost} | وضعیت پیدا می‌کند: {gained} | فایل: {opts['out']}")
