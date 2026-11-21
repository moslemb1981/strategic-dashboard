# -*- coding: utf-8 -*-
"""رنگ‌های جیغ و پررنگ ارزش‌های سازمانی فعلی را به پالت ملایم و هماهنگ با سامانه تبدیل می‌کند."""
from django.core.management.base import BaseCommand
from strategic.models import OrgValue

COLOR_MAP = {
    "#F59E0B": "#C97A2B",
    "#EC4899": "#1E6E7A",
    "#8B5CF6": "#6C56A3",
    "#0EA5E9": "#2E5C8A",
    "#F43F5E": "#B0413E",
    "#EAB308": "#D9A441",
    "#22C55E": "#3E7A52",
    "#A8557A": "#1E6E7A",  # اصلاح نسخه‌ی قبلی این دستور (رز خاکی → سرمه‌ای فیروزه‌ای)
    # A8321E (مرکز) تغییری نمی‌کنه، از قبل ملایم بوده
}


class Command(BaseCommand):
    help = "رنگ‌های جیغ قدیمی ارزش‌های سازمانی را به پالت ملایم جدید تبدیل می‌کند."

    def handle(self, *args, **options):
        updated = 0
        for v in OrgValue.objects.all():
            new_color = COLOR_MAP.get(v.color)
            if new_color:
                v.color = new_color
                v.save(update_fields=["color"])
                updated += 1
        self.stdout.write(self.style.SUCCESS(f"رنگ {updated} ارزش سازمانی به‌روزرسانی شد."))
