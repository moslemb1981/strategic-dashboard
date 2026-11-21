# -*- coding: utf-8 -*-
"""یکسان‌سازی نام دسته‌بندی «قوانین و الزامات» که یک رکورد قدیمی با نام کمی متفاوت
(«عوامل قوانین و الزامات») ثبت شده بود و باعث می‌شد گروه قانونی دوبار نمایش داده شود."""
from django.core.management.base import BaseCommand
from strategic.models import EnvironmentalFactor


class Command(BaseCommand):
    help = "نام دسته‌بندی «عوامل قوانین و الزامات» را با «قوانین و الزامات» یکسان می‌کند."

    def handle(self, *args, **options):
        n = EnvironmentalFactor.objects.filter(category="عوامل قوانین و الزامات").update(category="قوانین و الزامات")
        self.stdout.write(self.style.SUCCESS(f"اصلاح شد: {n} رکورد."))
