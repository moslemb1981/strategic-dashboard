# -*- coding: utf-8 -*-
"""بارگذاری داده‌ی نمونه‌ی اولیه برای هر ۱۰ دسته‌ی «هوش بازار» — تا کارشناسان دید درستی
از نوع و سطح داده‌ی موردنیاز داشته باشند. بعضی مقادیر (نرخ ارز، تورم، سود بانکی، آمار
تولید خودرو) برگرفته از منابع خبری واقعی و به‌روز هستند؛ بقیه (که علامت «نمونه» دارند)
مقادیر نمایشی‌اند و باید توسط کارشناس مربوطه با رقم واقعی جایگزین شوند.

این دستور idempotent نیست — هر بار اجرا، رکوردهای جدید اضافه می‌کند. برای اجرای مجدد
تمیز، اول رکوردهای قبلی رو دستی حذف کنید."""
import datetime
from django.core.management.base import BaseCommand
from strategic.models import (
    ExchangeRate, LegalTradeRequirement, VehicleMarketStat, EVTrend,
    CustomerSatisfactionBenchmark, SupplierCondition, InterestInflationRate,
    LaborMarketStat, DomesticRawMaterial,
)


class Command(BaseCommand):
    help = "داده‌ی نمونه‌ی اولیه (نزدیک به واقعیت) برای هر ۱۰ دسته‌ی هوش بازار بارگذاری می‌کند."

    def handle(self, *args, **options):
        today = datetime.date(2026, 8, 28)

        # ۱) نرخ ارز — واقعی، از TGJU.org (۶ شهریور ۱۴۰۵)
        ExchangeRate.objects.create(
            currency_name="دلار آزاد", value_rial=2006000, period_date=today,
            source_name="TGJU.org", note="نرخ بازار آزاد",
        )
        ExchangeRate.objects.create(
            currency_name="یورو", value_rial=2337000, period_date=today,
            source_name="TGJU.org", note="نرخ بازار آزاد",
        )

        # ۲) الزامات قانونی و تجاری — نمونه (باید با اطلاعیه‌ی رسمی جایگزین شود)
        LegalTradeRequirement.objects.create(
            title="[نمونه] بازنگری تعرفه‌ی واردات قطعات یدکی خودرو",
            item_type="domestic", announce_date=datetime.date(2026, 7, 15),
            effective_date=datetime.date(2026, 9, 1), organization="وزارت صمت / گمرک ایران",
            impact_level="high",
            description="نمونه‌ی نمایشی — لطفاً با آخرین اطلاعیه‌ی رسمی گمرک/وزارت صمت جایگزین شود.",
        )
        LegalTradeRequirement.objects.create(
            title="[نمونه] الزام درج شناسه کالا و کد رهگیری برای قطعات یدکی",
            item_type="domestic", announce_date=datetime.date(2026, 6, 1),
            effective_date=datetime.date(2026, 10, 1), organization="سازمان استاندارد ایران",
            impact_level="medium",
            description="نمونه‌ی نمایشی — الزام قانونی واقعی و در حال اجرا در صنعت، جزئیات دقیق باید تکمیل شود.",
        )

        # ۳) آمار تولید/فروش خودرو کشور — واقعی، مرداد ۱۴۰۵ (ایران‌خودرو + سایپا)
        VehicleMarketStat.objects.create(
            period_label="مرداد ۱۴۰۵", total_production=77000, total_sales=89000,
            brand_breakdown="مجموع ایران‌خودرو و سایپا؛ سه‌ماهه‌ی بهار ۱۴۰۵: سایپا ۴۳,۱۸۴ دستگاه (سهم حدود ۳۰٪)",
            source_name="گزارش‌های خبری مبتنی بر آمار وزارت صمت",
        )

        # ۴) روند خودروی برقی/هیبریدی — نمونه
        EVTrend.objects.create(
            period_label="[نمونه] سال ۱۴۰۵", ev_count=None,
            incentive_policies="نمونه — سیاست تشویقی مشخصی هنوز توسط کارشناس ثبت نشده",
            charging_infrastructure="نمونه — وضعیت زیرساخت شارژ هنوز توسط کارشناس ثبت نشده",
            source_name="",
        )

        # ۵) بنچمارک رضایت مشتری صنعت — نمونه (برای مقایسه با I10-I13 داخلی)
        CustomerSatisfactionBenchmark.objects.create(
            period_label="[نمونه] تابستان ۱۴۰۵", industry_avg_satisfaction=75.0,
            source_name="نمونه — منبع واقعی (مثلاً نظرسنجی انجمن صنفی) باید جایگزین شود",
            note="عدد نمایشی برای آشنایی با فرمت — لطفاً با بنچمارک واقعی صنعت جایگزین شود.",
        )

        # ۶) تأمین‌کنندگان بین‌المللی — نمونه‌ی نزدیک به واقعیت (بر پایه‌ی کشورهای شناخته‌شده)
        SupplierCondition.objects.create(
            country="چین", status="stable", delivery_time_days=45,
            local_currency_rate="یوان چین",
            description="بزرگ‌ترین منبع تأمین قطعات وارداتی؛ نسبتاً باثبات.",
        )
        SupplierCondition.objects.create(
            country="کره جنوبی", status="stable", delivery_time_days=35,
            local_currency_rate="وون کره",
            description="کیفیت بالاتر، قیمت نسبتاً بیشتر از چین.",
        )
        SupplierCondition.objects.create(
            country="ترکیه", status="risky", delivery_time_days=25,
            local_currency_rate="لیر ترکیه",
            description="نزدیک‌تر جغرافیایی (زمان تحویل کوتاه‌تر)، ولی نوسان لیر ریسک قیمتی ایجاد می‌کند.",
        )

        # ۷) نرخ سود بانکی و تورم — واقعی، مرداد ۱۴۰۵
        InterestInflationRate.objects.create(
            period_label="مرداد ۱۴۰۵", inflation_rate=89.0, bank_interest_rate=23.0,
            source_name="مرکز آمار ایران / شورای پول و اعتبار",
        )

        # ۸) بازار کار و دستمزد صنعت — نمونه
        LaborMarketStat.objects.create(
            period_label="[نمونه] مرداد ۱۴۰۵", job_role="کارشناس فروش قطعات یدکی",
            avg_industry_salary=None, turnover_rate=None,
            source_name="نمونه — رقم واقعی باید توسط واحد منابع انسانی/بنچمارک صنعت تکمیل شود",
        )

        # ۹) مواد اولیه‌ی داخلی — نمونه (رقم تخمینی، نیاز به تأیید با قیمت روز بورس کالا)
        DomesticRawMaterial.objects.create(
            material_name="[نمونه] فولاد (ورق روغنی)", price=850000, unit="کیلوگرم",
            period_label="مرداد ۱۴۰۵", source_name="[تخمینی — با قیمت روز بورس کالا جایگزین شود]",
        )

        self.stdout.write(self.style.SUCCESS(
            "داده‌ی نمونه برای هر ۱۰ دسته‌ی هوش بازار بارگذاری شد.\n"
            "موارد علامت‌خورده با «[نمونه]» یا توضیح «نمونه» باید با داده‌ی واقعی جایگزین شوند."
        ))
