"""بازگردانی نقشه‌ی استراتژیک «واسطه‌گری» از فایل پشتیبان JSON.

    python manage.py restore_brokerage_map --file backups/brokerage_map_20261111_120000.json           # فقط گزارش
    python manage.py restore_brokerage_map --file backups/brokerage_map_20261111_120000.json --apply   # اعمال

فایل پشتیبان را فرمان rebuild_brokerage_map_excellence پیش از هر تغییر خودکار می‌سازد.
قبل از بازگردانی، از وضعیت فعلی هم یک پشتیبان جدید گرفته می‌شود.
"""
import json

from django.core.management.base import BaseCommand, CommandError

from strategic.models import BusinessUnit
from ._bmap_io import restore, save_snapshot


class Command(BaseCommand):
    help = "بازگردانی نقشه‌ی استراتژیک واسطه‌گری از فایل پشتیبان"

    def add_arguments(self, parser):
        parser.add_argument("--file", required=True)
        parser.add_argument("--apply", action="store_true")

    def handle(self, *args, **opts):
        try:
            with open(opts["file"], encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            raise CommandError(f"فایل پشتیبان خوانده نشد: {e}")
        bu = BusinessUnit.objects.filter(name__contains="واسطه").first()
        if not bu:
            raise CommandError("کسب‌وکار «واسطه گری» پیدا نشد.")
        n = len(data["objectives"])
        self.stdout.write(f"پشتیبان مورخ {data['created']}: {n} کارت، رویکرد «{data['bu']['archetype']}».")
        if not opts["apply"]:
            self.stdout.write("حالت گزارش: چیزی تغییر نکرد. برای اعمال، --apply را اضافه کنید.")
            return
        path, _ = save_snapshot(bu, prefix="brokerage_map_before_restore")
        self.stdout.write(f"پشتیبان از وضعیت فعلی: {path}")
        restore(bu, data)
        self.stdout.write(self.style.SUCCESS(f"بازگردانی شد: {n} کارت."))
