# -*- coding: utf-8 -*-
"""جایگزینی استراتژی‌های وظیفه‌ای با فهرست نهایی (فایل اکسل «کل سازمان»).

    python manage.py replace_functional_strategies فایل.xlsx            # فقط گزارش (چیزی ذخیره نمی‌شود)
    python manage.py replace_functional_strategies فایل.xlsx --apply    # اعمال روی دیتابیس

قبل از --apply حتماً از db.sqlite3 نسخه پشتیبان بگیرید.

منطق:
- مدیریت‌ها به نام (بدون حساسیت به ی/ي، نیم‌فاصله و فاصله) پیدا می‌شوند.
- برای هر مدیریت، هر ردیف فایل با شبیه‌ترین استراتژی فعلیِ همان مدیریت جفت می‌شود؛ جفت‌ها در همان رکورد
  به‌روز می‌شوند، پس اتصال به اهداف نقشه و شاخص‌های عملیاتی حفظ می‌شود.
- ردیف بدون جفت ← استراتژی جدید (بدون اتصال)؛ استراتژی فعلی بدون جفت ← حذف.
- مدیریت‌هایی که در فایل نیستند (مثلاً بازرسی) دست‌نخورده می‌مانند."""
import csv
import re
from difflib import SequenceMatcher

import openpyxl
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from strategic.models import FunctionalStrategy, Management

# اصلاح نام‌های فایل → نام درست در سیستم
OWNER_FIX = {"انیار": "انبار"}
# تغییر نام مدیریت در سیستم (قبل ← بعد)
RENAMES = {"مدیریت ارتباطات": "مدیریت ارتباطات و افکارسنجی"}
THRESHOLD = 0.45


def _n(s):
    s = str(s or "").replace("ي", "ی").replace("ك", "ک").replace("أ", "ا").replace("ئ", "ی")
    return re.sub(r"[\s‌،,.؛:()]", "", s)


def _clean(s):
    return re.sub(r"\s+", " ", str(s or "").replace("‏", "")).strip()


class Command(BaseCommand):
    help = "جایگزینی استراتژی‌های وظیفه‌ای با فهرست نهایی اکسل"

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--report", default="fs_replace_report.csv")

    def handle(self, *args, **o):
        try:
            ws = openpyxl.load_workbook(o["path"], data_only=True).worksheets[0]
        except Exception as e:
            raise CommandError(f"فایل خوانده نشد: {e}")

        rows = {}
        for r in ws.iter_rows(min_row=2, values_only=True):
            owner, title = _clean(r[1]), _clean(r[2])
            if not owner or not title:
                continue
            for a, b in OWNER_FIX.items():
                owner = owner.replace(a, b)
            rows.setdefault(_n(owner), (owner, []))[1].append(title)

        mgmts = {}
        for m in Management.objects.select_related("org_unit"):
            nm = RENAMES.get(m.name, m.name)
            mgmts[_n(nm)] = m
        unknown = [v[0] for k, v in rows.items() if k not in mgmts]
        if unknown:
            raise CommandError("مدیریت ناشناخته در فایل: " + "؛ ".join(unknown))

        plan, rep = [], []
        for key, (owner, titles) in rows.items():
            m = mgmts[key]
            old = list(FunctionalStrategy.objects.filter(management_ref=m).order_by("order", "id"))
            pairs = []
            for ti, t in enumerate(titles):
                for oi, ob in enumerate(old):
                    pairs.append((SequenceMatcher(None, _n(t), _n(ob.title)).ratio(), ti, oi))
            pairs.sort(reverse=True)
            used_t, used_o, match = set(), set(), {}
            for sc, ti, oi in pairs:
                if sc < THRESHOLD:
                    break
                if ti in used_t or oi in used_o:
                    continue
                used_t.add(ti); used_o.add(oi); match[ti] = (old[oi], sc)
            for ti, t in enumerate(titles):
                if ti in match:
                    ob, sc = match[ti]
                    kind = "بدون تغییر" if _n(ob.title) == _n(t) else "به‌روزرسانی"
                    rep.append([m.name, kind, round(sc, 2), ob.title, t,
                                ob.linked_objectives.count(), ob.linked_operational_kpis.count()])
                    plan.append(("upd", m, ob, t, ti + 1))
                else:
                    rep.append([m.name, "جدید", "", "", t, 0, 0])
                    plan.append(("new", m, None, t, ti + 1))
            for oi, ob in enumerate(old):
                if oi not in used_o:
                    rep.append([m.name, "حذف", "", ob.title, "", ob.linked_objectives.count(), ob.linked_operational_kpis.count()])
                    plan.append(("del", m, ob, "", 0))

        with open(o["report"], "w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["مدیریت", "عملیات", "شباهت", "متن فعلی", "متن جدید", "اتصال به هدف", "اتصال به شاخص"])
            w.writerows(rep)

        cnt = {k: sum(1 for p in plan if p[0] == k) for k in ("upd", "new", "del")}
        lost_o = sum(r[5] for r in rep if r[1] == "حذف")
        lost_k = sum(r[6] for r in rep if r[1] == "حذف")
        self.stdout.write(f"به‌روزرسانی: {cnt['upd']} — جدید: {cnt['new']} — حذف: {cnt['del']} "
                          f"(اتصال هدف/شاخصِ ردیف‌های حذفی: {lost_o}/{lost_k})")
        self.stdout.write(f"گزارش کامل: {o['report']}")
        if not o["apply"]:
            self.stdout.write(self.style.WARNING("حالت آزمایشی — چیزی ذخیره نشد. برای اعمال: --apply"))
            return

        with transaction.atomic():
            for old_name, new_name in RENAMES.items():
                for m in Management.objects.filter(name=old_name):
                    m.name = new_name
                    m.save()
            for kind, m, ob, t, order in plan:
                m.refresh_from_db()
                if kind == "upd":
                    ob.title, ob.order, ob.management = t, order, m.name
                    ob.save()
                elif kind == "new":
                    FunctionalStrategy.objects.create(org_unit=m.org_unit, management=m.name, title=t, order=order)
                else:
                    ob.delete()
        self.stdout.write(self.style.SUCCESS("اعمال شد."))
