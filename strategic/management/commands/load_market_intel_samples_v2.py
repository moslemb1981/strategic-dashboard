# -*- coding: utf-8 -*-
"""تکمیل داده‌ی نمونه برای ۳ دسته‌ی تازه‌اضافه‌شده‌ی «هوش بازار»
(نرخ تسهیلات خودرو، واردات/صادرات قطعات، قطعات راهبردی/الکترونیک)."""
from django.core.management.base import BaseCommand
from strategic.models import VehicleLoanRate, VehiclePartsTradeStat, StrategicElectronicPart


class Command(BaseCommand):
    help = "داده‌ی نمونه برای ۳ دسته‌ی تازه‌ی هوش بازار (تسهیلات خودرو، واردات/صادرات، قطعات راهبردی) بارگذاری می‌کند."

    def handle(self, *args, **options):
        VehicleLoanRate.objects.create(
            period_label="مرداد ۱۴۰۵", interest_rate=23.0, max_loan_amount=None,
            mandatory_down_payment_pct=None,
            source_name="[تخمینی بر پایه‌ی نرخ عمومی تسهیلات بانکی — با نرخ خاص وام خودرو جایگزین شود]",
        )
        VehiclePartsTradeStat.objects.create(
            period_label="[نمونه] مرداد ۱۴۰۵", imported_vehicle_count=None,
            parts_import_value=None, parts_export_value=None,
            origin_destination="چین (مبدأ عمده‌ی نمونه)",
            source_name="نمونه — رقم واقعی از گمرک ایران باید ثبت شود",
        )
        StrategicElectronicPart.objects.create(
            part_name="[نمونه] ECU موتور", global_inventory_note="نمونه — وضعیت واقعی موجودی جهانی باید ثبت شود",
            delivery_time_days=None, price_usd=None, status="normal", source_name="",
        )
        self.stdout.write(self.style.SUCCESS("داده‌ی نمونه برای هر ۳ دسته‌ی جدید بارگذاری شد."))
