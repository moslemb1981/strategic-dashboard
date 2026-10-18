"""اتصال شاخص‌های عملیاتی به استراتژی‌های وظیفه‌ای (یک‌بار مصرف، با پیش‌نمایش).

منطق: برای هر استراتژی وظیفه‌ای، از میان شاخص‌های عملیاتیِ اهداف نقشه‌ی وصل‌شده به آن،
فقط شاخص‌هایی که «دپارتمان مالک» آن‌ها با نام همان مدیریت می‌خواند پیشنهاد می‌شود.
شاخص‌های عملیاتی که هیچ استراتژی وظیفه‌ای مدیریت مالکشان را نگرفته‌اند در گزارش می‌آیند.

اجرا:
  python manage.py link_functional_strategy_kpis            # فقط گزارش (بدون نوشتن)
  python manage.py link_functional_strategy_kpis --apply    # اعمال روی پایگاه داده
"""
import csv
import re

from django.core.management.base import BaseCommand

from strategic.models import FunctionalStrategy, OperationalKPI


def norm(s):
    s = (s or "").replace("ي", "ی").replace("ك", "ک").replace("‌", " ")
    s = re.sub(r"[\s‌]+", " ", s).strip()
    s = re.sub(r"^(مدیریت|معاونت)( های| ها)?\s+", "", s)
    s = re.sub(r"\s*و\s+", " و ", s)
    return s


class Command(BaseCommand):
    help = "اتصال شاخص‌های عملیاتی به استراتژی‌های وظیفه‌ای بر اساس هدف مرتبط و مدیریت مالک (پیش‌فرض: فقط گزارش)"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="تغییرات را در پایگاه داده ذخیره کن")
        parser.add_argument("--report", default="fs_kpi_link_report.csv", help="مسیر فایل گزارش CSV")

    def handle(self, *args, **opts):
        apply_ = opts["apply"]
        fss = list(FunctionalStrategy.objects.prefetch_related(
            "linked_objectives__linked_operational_kpis", "linked_operational_kpis"))
        by_mgmt = {}
        for fs in fss:
            by_mgmt.setdefault(norm(fs.management), []).append(fs)

        linked_pairs, rows = set(), []
        added = 0
        for fs in fss:
            m = norm(fs.management)
            cand = {}
            for o in fs.linked_objectives.all():
                for k in o.linked_operational_kpis.all():
                    if norm(k.department) == m:
                        cand[k.pk] = k
            existing = {k.pk for k in fs.linked_operational_kpis.all()}
            for pk, k in cand.items():
                linked_pairs.add(pk)
                if pk not in existing:
                    added += 1
                    rows.append((fs.management, fs.title, k.code, k.title, k.department, "پیشنهاد اتصال"))
            if apply_ and cand:
                fs.linked_operational_kpis.add(*cand.keys())
            if not cand and not existing:
                rows.append((fs.management, fs.title, "", "", "", "استراتژی بدون شاخص (نیاز به انتخاب دستی)"))

        # شاخص‌هایی که به هیچ استراتژی وصل نشده‌اند
        all_linked = set(linked_pairs)
        for fs in fss:
            all_linked |= {k.pk for k in fs.linked_operational_kpis.all()}
        orphan = 0
        for k in OperationalKPI.objects.all():
            if k.pk in all_linked:
                continue
            orphan += 1
            has_mgmt = norm(k.department) in by_mgmt
            note = ("مدیریت مالک استراتژی دارد؛ به یکی از استراتژی‌هایش وصل کنید" if has_mgmt
                    else "هیچ استراتژی وظیفه‌ای برای مدیریت مالک ثبت نشده")
            rows.append(("", "", k.code, k.title, k.department, "شاخص بدون استراتژی: " + note))

        with open(opts["report"], "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["مدیریت", "استراتژی وظیفه‌ای", "کد شاخص", "عنوان شاخص", "دپارتمان مالک", "وضعیت"])
            w.writerows(rows)

        self.stdout.write(f"استراتژی وظیفه‌ای: {len(fss)} | اتصال جدید: {added} | شاخص‌های بدون استراتژی: {orphan}")
        self.stdout.write(("اعمال شد." if apply_ else "فقط گزارش (چیزی ذخیره نشد؛ برای اعمال --apply بزنید).")
                          + f" گزارش: {opts['report']}")
