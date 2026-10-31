# -*- coding: utf-8 -*-
"""اصلاح دو جفتِ اشتباهِ تطبیق خودکار (بعد از replace_functional_strategies).

    python manage.py fix_fs_pairs                         # اتصال‌های اشتباه را خالی می‌کند
    python manage.py fix_fs_pairs --backup db_backup.sqlite3   # اتصال‌های درست را از نسخه پشتیبان برمی‌گرداند

بدون --apply فقط گزارش می‌دهد."""
import sqlite3

from django.core.management.base import BaseCommand
from django.db import transaction

from strategic.models import FunctionalStrategy

# (عنوان استراتژی جدید در سیستم [ابتدای متن]، ابتدای عنوان استراتژی قدیمیِ درست در نسخه پشتیبان)
CASES = [
    ("کنترل صحت عملکرد تجهیزات تعمیرگاهی", "مدیریت و کنترل هزینه فرآیندهای نگهداری"),
    ("توسعه نظام یکپارچه سلامت، ایمنی کارکنان", "کاهش ضریب شدت تکرار حوادث ناشی از کار"),
]


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--backup", default="")
        parser.add_argument("--apply", action="store_true")

    def handle(self, *a, **o):
        con = sqlite3.connect(o["backup"]) if o["backup"] else None
        with transaction.atomic():
            for new_start, old_start in CASES:
                fs = FunctionalStrategy.objects.filter(title__startswith=new_start).first()
                if not fs:
                    self.stdout.write(f"پیدا نشد: {new_start}")
                    continue
                objs, kpis = [], []
                if con:
                    row = con.execute("select id from strategic_functionalstrategy where title like ?", (old_start + "%",)).fetchone()
                    if row:
                        objs = [r[0] for r in con.execute("select strategicobjective_id from strategic_functionalstrategy_linked_objectives where functionalstrategy_id=?", (row[0],))]
                        kpis = [r[0] for r in con.execute("select operationalkpi_id from strategic_functionalstrategy_linked_operational_kpis where functionalstrategy_id=?", (row[0],))]
                    else:
                        self.stdout.write(f"در نسخه پشتیبان پیدا نشد: {old_start}")
                self.stdout.write(f"{fs.management} | {fs.title[:50]}: اتصال فعلی {fs.linked_objectives.count()}/{fs.linked_operational_kpis.count()} ← جدید {len(objs)}/{len(kpis)}")
                fs.linked_objectives.set(objs)
                fs.linked_operational_kpis.set(kpis)
            if not o["apply"]:
                transaction.set_rollback(True)
                self.stdout.write("حالت آزمایشی — چیزی ذخیره نشد. برای اعمال: --apply")
            else:
                self.stdout.write("اعمال شد.")
