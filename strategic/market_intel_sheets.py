# -*- coding: utf-8 -*-
"""مشخصات هر ۱۳ شیت اکسل «هوش بازار» — یه‌جا تعریف شده تا هم اکسپورت هم ایمپورت
از همین لیست استفاده کنن (بدون تکرار کد برای هر دسته).

هر ستون: (برچسب فارسی، نام فیلد مدل، نوع) — نوع یکی از:
  "text" | "number" | "decimal" | "jalali_date" | "choice"
برای "choice"، یه دیکشنری {مقدار_داخلی: برچسب_فارسی} هم لازمه (choices_map).

natural_key: لیست فیلدهایی که با هم، یه رکورد رو یکتا مشخص می‌کنن — موقع ایمپورت،
اگه رکوردی با همین ترکیب پیدا بشه، به‌روزرسانی می‌شه، وگرنه رکورد جدید ساخته می‌شه."""


def get_sheet_specs():
    from .models import (
        ExchangeRate, LegalTradeRequirement, VehicleMarketStat, EVTrend,
        CustomerSatisfactionBenchmark, SupplierCondition, InterestInflationRate,
        LaborMarketStat, DomesticRawMaterial, VehicleLoanRate, VehiclePartsTradeStat,
        StrategicElectronicPart, MarketIntelReport,
    )

    return [
        {
            "sheet_name": "نرخ ارز", "model": ExchangeRate, "natural_key": ["currency_name", "period_date"],
            "columns": [
                ("نام ارز", "currency_name", "text"),
                ("نرخ (ریال)", "value_rial", "decimal"),
                ("تاریخ (شمسی)", "period_date", "jalali_date"),
                ("منبع", "source_name", "text"),
                ("توضیح", "note", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "الزامات قانونی و تجاری", "model": LegalTradeRequirement, "natural_key": ["title"],
            "columns": [
                ("عنوان", "title", "text"),
                ("نوع", "item_type", "choice", dict(LegalTradeRequirement.TYPE_CHOICES)),
                ("تاریخ ابلاغ (شمسی)", "announce_date", "jalali_date"),
                ("تاریخ اجرا/مهلت (شمسی)", "effective_date", "jalali_date"),
                ("سازمان", "organization", "text"),
                ("سطح اثر", "impact_level", "choice", dict(LegalTradeRequirement.IMPACT_CHOICES)),
                ("توضیح", "description", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "آمار خودرو کشور", "model": VehicleMarketStat, "natural_key": ["period_label"],
            "columns": [
                ("دوره", "period_label", "text"),
                ("تولید کل کشور", "total_production", "number"),
                ("فروش کل کشور", "total_sales", "number"),
                ("تفکیک برند", "brand_breakdown", "text"),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "روند خودروی برقی-هیبریدی", "model": EVTrend, "natural_key": ["period_label"],
            "columns": [
                ("دوره", "period_label", "text"),
                ("تعداد ثبت‌شده", "ev_count", "number"),
                ("سیاست‌های تشویقی", "incentive_policies", "text"),
                ("زیرساخت شارژ", "charging_infrastructure", "text"),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "بنچمارک رضایت مشتری", "model": CustomerSatisfactionBenchmark, "natural_key": ["period_label"],
            "columns": [
                ("دوره", "period_label", "text"),
                ("میانگین رضایت صنعت", "industry_avg_satisfaction", "decimal"),
                ("منبع", "source_name", "text"),
                ("توضیح", "note", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "تأمین‌کنندگان", "model": SupplierCondition, "natural_key": ["supplier_type", "country"],
            "columns": [
                ("نوع تأمین‌کننده", "supplier_type", "choice", dict(SupplierCondition.SUPPLIER_TYPE_CHOICES)),
                ("کشور/منطقه", "country", "text"),
                ("وضعیت", "status", "choice", dict(SupplierCondition.STATUS_CHOICES)),
                ("زمان تحویل (روز)", "delivery_time_days", "number"),
                ("نرخ ارز محلی", "local_currency_rate", "text"),
                ("توضیح", "description", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "سود بانکی و تورم", "model": InterestInflationRate, "natural_key": ["period_label"],
            "columns": [
                ("دوره", "period_label", "text"),
                ("نرخ تورم (٪)", "inflation_rate", "decimal"),
                ("نرخ سود بانکی (٪)", "bank_interest_rate", "decimal"),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "بازار کار صنعت", "model": LaborMarketStat, "natural_key": ["period_label", "job_role"],
            "columns": [
                ("دوره", "period_label", "text"),
                ("رده شغلی", "job_role", "text"),
                ("میانگین حقوق (ریال)", "avg_industry_salary", "decimal"),
                ("نرخ ترک شغل (٪)", "turnover_rate", "decimal"),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "مواد اولیه داخلی", "model": DomesticRawMaterial, "natural_key": ["material_name", "period_label"],
            "columns": [
                ("نام ماده", "material_name", "text"),
                ("نوع کاربرد", "usage_type", "text"),
                ("قیمت (ریال)", "price", "decimal"),
                ("واحد", "unit", "text"),
                ("نوسان ماهانه (٪)", "monthly_fluctuation_pct", "decimal"),
                ("دوره", "period_label", "text"),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "تسهیلات خرید خودرو", "model": VehicleLoanRate, "natural_key": ["period_label"],
            "columns": [
                ("دوره", "period_label", "text"),
                ("نرخ سود (٪)", "interest_rate", "decimal"),
                ("حداکثر مبلغ وام (ریال)", "max_loan_amount", "decimal"),
                ("پیش‌پرداخت اجباری (٪)", "mandatory_down_payment_pct", "decimal"),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "واردات-صادرات قطعات و خودرو", "model": VehiclePartsTradeStat, "natural_key": ["period_label"],
            "columns": [
                ("دوره", "period_label", "text"),
                ("تعداد خودروی وارداتی", "imported_vehicle_count", "number"),
                ("ارزش واردات قطعات (دلار)", "parts_import_value", "decimal"),
                ("ارزش صادرات قطعات (دلار)", "parts_export_value", "decimal"),
                ("کشور مبدأ/مقصد", "origin_destination", "text"),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "قطعات راهبردی و الکترونیک", "model": StrategicElectronicPart, "natural_key": ["part_name"],
            "columns": [
                ("نام قطعه", "part_name", "text"),
                ("موجودی انبار جهانی", "global_inventory_note", "text"),
                ("زمان تحویل (روز)", "delivery_time_days", "number"),
                ("قیمت (دلار)", "price_usd", "decimal"),
                ("وضعیت", "status", "choice", dict(StrategicElectronicPart.STATUS_CHOICES)),
                ("منبع", "source_name", "text"),
                ("تحلیل کارشناس", "analyst_note", "text"),
            ],
        },
        {
            "sheet_name": "گزارش تحلیلی دوره‌ای", "model": MarketIntelReport, "natural_key": ["title"],
            "columns": [
                ("عنوان گزارش", "title", "text"),
                ("دوره", "period_label", "text"),
                ("تاریخ گزارش (شمسی)", "report_date", "jalali_date"),
                ("خلاصه اجرایی", "summary", "text"),
                ("متن کامل تحلیل", "content", "text"),
                ("ریسک‌های کلیدی", "key_risks", "text"),
                ("فرصت‌های کلیدی", "key_opportunities", "text"),
                ("اقدامات پیشنهادی", "recommended_actions", "text"),
            ],
        },
    ]
