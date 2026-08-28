# -*- coding: utf-8 -*-
"""تکمیل نهایی داده‌ی نمونه‌ی هوش بازار: افزودن «تحلیل/برداشت کارشناس» به هر رکورد
موجود (تا کارشناسان الگوی درست نوشتن تحلیل رو ببینن)، به‌علاوه ۲ گزارش تحلیلی
دوره‌ای نمونه که همه‌ی دسته‌ها رو کنار هم روایت می‌کنه."""
import datetime
from django.core.management.base import BaseCommand
from strategic.models import (
    ExchangeRate, LegalTradeRequirement, VehicleMarketStat, EVTrend,
    CustomerSatisfactionBenchmark, SupplierCondition, InterestInflationRate,
    LaborMarketStat, DomesticRawMaterial, VehicleLoanRate, VehiclePartsTradeStat,
    StrategicElectronicPart, MarketIntelReport,
)


class Command(BaseCommand):
    help = "تحلیل کارشناس نمونه به رکوردهای موجود هوش بازار اضافه می‌کند و ۲ گزارش تحلیلی نمونه می‌سازد."

    def handle(self, *args, **options):
        notes_map = {
            (ExchangeRate, "دلار آزاد"): "افزایش تدریجی نرخ دلار طی سه ماه اخیر، فشار مستقیمی بر قیمت تمام‌شده‌ی قطعات وارداتی وارد می‌کند. پیشنهاد می‌شود بخش بازرگانی، سفارش‌های بزرگ را زودتر از موعد نهایی کند.",
            (ExchangeRate, "یورو"): "نوسان یورو نسبت به دلار محدودتر بوده؛ برای تأمین‌کنندگان اروپایی (در صورت وجود)، ریسک ارزی نسبتاً کنترل‌شده است.",
            (VehicleMarketStat, None): "رشد تولید و فروش خودرو کشور در مرداد، نشانه‌ی مثبتی برای تقاضای آتی قطعات یدکی و خدمات پس از فروش است — به‌ویژه برای قطعات مرتبط با گارانتی اولیه.",
            (InterestInflationRate, None): "تورم بالای ۸۹٪ به‌طور مستقیم روی قدرت خرید مصرف‌کننده و تمایل به تعویق تعمیرات غیرضروری اثر می‌گذارد؛ باید در پیش‌بینی فروش خدمات درجه‌دو لحاظ شود.",
            (DomesticRawMaterial, "[نمونه] فولاد (ورق روغنی)"): "نوسان قیمت فولاد مستقیماً روی هزینه‌ی تمام‌شده‌ی قطعات بدنه اثر دارد. توصیه می‌شود قراردادهای بلندمدت با تأمین‌کنندگان داخلی برای ثبات قیمت بررسی شود.",
        }
        updated = 0
        for (model, key), note in notes_map.items():
            qs = model.objects.filter(currency_name=key) if key and hasattr(model, "currency_name") else \
                 model.objects.filter(material_name=key) if key and hasattr(model, "material_name") else \
                 model.objects.all()
            for obj in qs:
                obj.analyst_note = note
                obj.save(update_fields=["analyst_note"])
                updated += 1

        # چندتا تحلیل نمونه‌ی دیگر برای دسته‌هایی که فیلد شناسایی ساده‌تری دارن
        for obj in LegalTradeRequirement.objects.all()[:1]:
            obj.analyst_note = "در صورت اجرایی‌شدن، هزینه‌ی واردات برای دسته‌ی قطعات مرتبط تا حدود ۱۰-۱۵٪ افزایش می‌یابد — نیاز به بازنگری قیمت فروش نهایی."
            obj.save(update_fields=["analyst_note"])
            updated += 1
        for obj in SupplierCondition.objects.filter(country="ترکیه"):
            obj.analyst_note = "نوسان لیر ترکیه در ۶ ماه اخیر باعث نوسان قیمت خرید تا ۱۲٪ شده — پیشنهاد می‌شود بخشی از حجم خرید از این تأمین‌کننده به چین منتقل شود."
            obj.save(update_fields=["analyst_note"])
            updated += 1
        for obj in StrategicElectronicPart.objects.all()[:1]:
            obj.analyst_note = "کمبود جهانی این قطعه می‌تواند زمان تعمیر خودروهای دارای این قطعه را تا ۲ برابر افزایش دهد — نیاز به موجودی احتیاطی بیشتر در انبار مرکزی."
            obj.save(update_fields=["analyst_note"])
            updated += 1

        # ۲ گزارش تحلیلی دوره‌ای نمونه
        MarketIntelReport.objects.create(
            title="گزارش تحلیلی هوش بازار — مرداد ۱۴۰۵",
            period_label="مرداد ۱۴۰۵", report_date=datetime.date(2026, 8, 28),
            summary="نرخ ارز و تورم بالا فشار هزینه‌ای وارد می‌کنند؛ در مقابل، رشد تولید/فروش خودرو کشور چشم‌انداز تقاضای قطعات یدکی را مثبت نگه می‌دارد.",
            content=(
                "در این دوره، نرخ دلار آزاد به ۲,۰۰۶,۰۰۰ ریال رسید که نسبت به دوره‌ی قبل رشد محسوسی داشته است. "
                "این افزایش، همراه با تورم نقطه‌به‌نقطه‌ی ۸۹٪، فشار مضاعفی بر هزینه‌ی تمام‌شده‌ی قطعات وارداتی و "
                "توان خرید مشتریان نهایی وارد می‌کند.\n\n"
                "در طرف مقابل، آمار تولید و فروش خودرو کشور (۷۷ هزار تولید، ۸۹ هزار فروش در مرداد) نشان‌دهنده‌ی "
                "رونق نسبی بازار خودروست که در میان‌مدت به معنای افزایش تقاضای خدمات گارانتی و قطعات یدکی خواهد بود.\n\n"
                "در حوزه‌ی تأمین‌کنندگان بین‌المللی، وضعیت چین و کره جنوبی باثبات ارزیابی می‌شود؛ ترکیه به‌دلیل "
                "نوسان لیر در وضعیت پرریسک‌تری قرار دارد."
            ),
            key_risks="افزایش مستمر نرخ ارز و تورم؛ نوسان لیر ترکیه برای تأمین‌کنندگان مرتبط؛ کمبود احتمالی قطعات الکترونیک راهبردی.",
            key_opportunities="رشد بازار خودرو کشور به‌معنای افزایش تقاضای بالقوه‌ی خدمات پس‌ازفروش و قطعات گارانتی.",
            recommended_actions="بررسی قراردادهای بلندمدت با تأمین‌کنندگان داخلی فولاد؛ کاهش وابستگی به تأمین‌کننده‌ی ترکیه‌ای؛ افزایش موجودی احتیاطی قطعات الکترونیک حساس.",
        )

        self.stdout.write(self.style.SUCCESS(
            f"تحلیل کارشناس به {updated} رکورد اضافه شد؛ ۱ گزارش تحلیلی دوره‌ای نمونه هم ساخته شد."
        ))
