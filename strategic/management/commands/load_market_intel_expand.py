# -*- coding: utf-8 -*-
"""افزایش چشمگیر حجم داده‌ی نمونه‌ی هوش بازار — چند دوره‌ی زمانی برای هر دسته
(تا نشانگر روند واقعاً چیزی برای نمایش داشته باشد) + تحلیل‌های کارشناسی مفصل‌تر
و واقع‌گرایانه‌تر (نه فقط یک جمله)."""
import datetime
from django.core.management.base import BaseCommand
from strategic.models import (
    ExchangeRate, LegalTradeRequirement, VehicleMarketStat, EVTrend,
    CustomerSatisfactionBenchmark, SupplierCondition, InterestInflationRate,
    LaborMarketStat, DomesticRawMaterial, VehicleLoanRate, VehiclePartsTradeStat,
    StrategicElectronicPart, MarketIntelReport,
)


class Command(BaseCommand):
    help = "حجم داده‌ی نمونه‌ی هوش بازار را به‌طور چشمگیر افزایش می‌دهد (چند دوره + تحلیل مفصل)."

    def handle(self, *args, **options):
        LONG_NOTE_1 = (
            "روند صعودی نرخ دلار در سه ماه اخیر، مستقیماً بر ساختار هزینه‌ی تمام‌شده‌ی قطعات وارداتی اثر گذاشته "
            "است. بر اساس بررسی سبد خرید فصل گذشته، حدود ۴۰٪ از اقلام پرگردش شرکت منشأ وارداتی دارند؛ بنابراین "
            "هر ۱٪ افزایش نرخ ارز، به‌طور میانگین ۰.۴٪ افزایش مستقیم در بهای تمام‌شده‌ی این دسته از کالاها ایجاد "
            "می‌کند. با توجه به این‌که تعدیل قیمت فروش معمولاً با یک تا دو ماه تأخیر نسبت به نرخ ارز انجام می‌شود، "
            "پیشنهاد می‌شود واحد بازرگانی برای اقلام حساس (به‌ویژه قطعات الکترونیکی و گارانتی)، سیاست پوشش ریسک "
            "ارزی (مانند قفل نرخ در قراردادهای بلندمدت) را بررسی کند. همچنین لازم است هماهنگی نزدیک‌تری با واحد "
            "فروش برای به‌روزرسانی به‌موقع لیست قیمت صورت گیرد تا حاشیه‌ی سود از بین نرود."
        )
        LONG_NOTE_2 = (
            "رشد تولید و فروش خودرو در سطح کشور، به‌ویژه از سوی دو خودروساز اصلی، نشانه‌ی خوبی برای تقاضای "
            "آتی خدمات پس از فروش و قطعات یدکی گارانتی است. با توجه به این‌که میانگین ورود خودرو به بازه‌ی "
            "نیاز به خدمات دوره‌ای حدود ۶ تا ۱۲ ماه پس از فروش است، انتظار می‌رود اثر این رشد در دو تا سه فصل "
            "آینده در حجم مراجعات تعمیرگاهی و فروش قطعات گارانتی منعکس شود. توصیه می‌شود واحد برنامه‌ریزی "
            "زنجیره‌ی تأمین، پیش‌بینی موجودی قطعات پرمصرف اولیه (فیلتر، روغن، لنت ترمز) را متناسب با این رشد "
            "به‌روزرسانی کند تا در فصل‌های آینده با کمبود موجودی مواجه نشویم."
        )
        LONG_NOTE_3 = (
            "تورم بالای اقتصاد کشور، به‌طور مستقیم بر تصمیم مشتریان برای تعویق تعمیرات غیرضروری و انتخاب قطعات "
            "ارزان‌تر (اغلب غیراستاندارد یا بازار غیررسمی) اثر می‌گذارد. این روند در میان‌مدت می‌تواند سهم بازار "
            "بخش «بازار غیررسمی/تقلبی» را افزایش دهد — دقیقاً همان ریسکی که در پروفایل این رقیب ثبت شده است. "
            "از سوی دیگر، نرخ سود بانکی بالا هزینه‌ی تأمین مالی برای طرح‌های فروش اقساطی (مانند کارت طلایی) را "
            "افزایش می‌دهد. پیشنهاد می‌شود بسته‌های تشویقی برای حفظ مشتریان حساس به قیمت (مثل تخفیف‌های فصلی یا "
            "برنامه‌ی وفاداری) در دستور کار قرار گیرد، هم‌زمان با تدوین کمپین آگاهی‌بخشی درباره‌ی ریسک‌های قطعات "
            "غیراستاندارد برای حفظ جایگاه برند."
        )

        # ===== ۱) نرخ ارز — چند دوره برای هر دو ارز (برای نمایش روند واقعی) =====
        dollar_series = [
            (datetime.date(2026, 6, 6), 1780000),
            (datetime.date(2026, 7, 6), 1890000),
            (datetime.date(2026, 8, 6), 1950000),
            (datetime.date(2026, 8, 28), 2006000),
        ]
        for d, v in dollar_series:
            ExchangeRate.objects.update_or_create(
                currency_name="دلار آزاد", period_date=d,
                defaults={"value_rial": v, "source_name": "TGJU.org",
                          "analyst_note": LONG_NOTE_1 if d == dollar_series[-1][0] else ""},
            )
        euro_series = [
            (datetime.date(2026, 7, 6), 2150000),
            (datetime.date(2026, 8, 6), 2280000),
            (datetime.date(2026, 8, 28), 2337000),
        ]
        for d, v in euro_series:
            ExchangeRate.objects.update_or_create(
                currency_name="یورو", period_date=d,
                defaults={"value_rial": v, "source_name": "TGJU.org"},
            )

        # ===== ۲) الزامات قانونی و تجاری — ۲ مورد بیشتر =====
        LegalTradeRequirement.objects.get_or_create(
            title="بازنگری استاندارد ایمنی قطعات ترمز خودرو", item_type="domestic",
            defaults={
                "announce_date": datetime.date(2026, 5, 10), "effective_date": datetime.date(2026, 11, 1),
                "organization": "سازمان استاندارد ایران", "impact_level": "medium",
                "description": "الزام تطبیق قطعات ترمزی وارداتی و داخلی با استاندارد جدید ایمنی.",
            },
        )
        LegalTradeRequirement.objects.get_or_create(
            title="تمدید مجوز واردات موقت قطعات یدکی از کره جنوبی", item_type="international",
            defaults={
                "announce_date": datetime.date(2026, 8, 1), "effective_date": datetime.date(2026, 8, 15),
                "organization": "وزارت صمت", "impact_level": "low",
                "description": "تمدید ۶ ماهه‌ی مجوز واردات موقت برای تسهیل تأمین قطعات از کره جنوبی.",
            },
        )

        # ===== ۳) آمار خودرو کشور — چند دوره =====
        vms_series = [
            ("خرداد ۱۴۰۵", 68000, 79000), ("تیر ۱۴۰۵", 71000, 83000), ("مرداد ۱۴۰۵", 77000, 89000),
        ]
        for period, prod, sale in vms_series:
            VehicleMarketStat.objects.update_or_create(
                period_label=period,
                defaults={
                    "total_production": prod, "total_sales": sale,
                    "brand_breakdown": "مجموع ایران‌خودرو و سایپا؛ سهم گروه سایپا حدود ۳۰٪",
                    "source_name": "گزارش‌های خبری مبتنی بر آمار وزارت صمت",
                    "analyst_note": LONG_NOTE_2 if period == "مرداد ۱۴۰۵" else "",
                },
            )

        # ===== ۴) روند خودروی برقی/هیبریدی — ۱ مورد دیگر =====
        EVTrend.objects.get_or_create(
            period_label="بهار ۱۴۰۵",
            defaults={
                "ev_count": 3200,
                "incentive_policies": "معافیت بخشی از عوارض گمرکی برای واردات خودروی برقی زیر سقف قیمتی مصوب.",
                "charging_infrastructure": "تعداد ایستگاه‌های شارژ عمومی در کلان‌شهرها همچنان محدود و عمدتاً در تهران متمرکز است.",
                "source_name": "[نمونه]",
            },
        )

        # ===== ۵) بنچمارک رضایت مشتری — ۱ مورد دیگر =====
        CustomerSatisfactionBenchmark.objects.get_or_create(
            period_label="بهار ۱۴۰۵",
            defaults={"industry_avg_satisfaction": 72.0, "source_name": "[نمونه]",
                      "note": "میانگین صنعت با نوسان جزئی نسبت به فصل قبل."},
        )

        # ===== ۶) تأمین‌کنندگان — افزودن حداقل ۱ داخلی =====
        SupplierCondition.objects.get_or_create(
            supplier_type="domestic", country="استان اصفهان",
            defaults={
                "status": "stable", "delivery_time_days": 7,
                "description": "قطب صنعتی قطعه‌سازی کشور با چندین تأمین‌کننده‌ی معتبر برای قطعات فلزی و پلاستیکی.",
                "analyst_note": "ظرفیت تولید تأمین‌کنندگان اصفهان طی سال گذشته حدود ۱۵٪ رشد کرده و می‌تواند بخشی از وابستگی به واردات چین را برای قطعات ساده‌تر (مانند براکت و پوسته) کاهش دهد.",
            },
        )
        SupplierCondition.objects.get_or_create(
            supplier_type="domestic", country="استان تهران",
            defaults={"status": "stable", "delivery_time_days": 3,
                      "description": "نزدیک‌ترین تأمین‌کنندگان از نظر جغرافیایی؛ عمدتاً قطعات کوچک و نهایی‌سازی."},
        )
        for s in SupplierCondition.objects.filter(country="ترکیه"):
            s.analyst_note = LONG_NOTE_3
            s.save(update_fields=["analyst_note"])

        # ===== ۷) نرخ سود بانکی و تورم — چند دوره =====
        infl_series = [
            ("خرداد ۱۴۰۵", 78.0, 23.0), ("تیر ۱۴۰۵", 83.0, 23.0), ("مرداد ۱۴۰۵", 89.0, 23.0),
        ]
        for period, infl, bank in infl_series:
            InterestInflationRate.objects.update_or_create(
                period_label=period,
                defaults={"inflation_rate": infl, "bank_interest_rate": bank,
                          "source_name": "مرکز آمار ایران / شورای پول و اعتبار",
                          "analyst_note": LONG_NOTE_3 if period == "مرداد ۱۴۰۵" else ""},
            )

        # ===== ۸) بازار کار — چند دوره برای همون رده شغلی =====
        labor_series = [("خرداد ۱۴۰۵", 145000000), ("تیر ۱۴۰۵", 152000000), ("مرداد ۱۴۰۵", 158000000)]
        for period, salary in labor_series:
            LaborMarketStat.objects.update_or_create(
                period_label=period, job_role="کارشناس فروش قطعات یدکی",
                defaults={"avg_industry_salary": salary, "turnover_rate": 12.5,
                          "source_name": "[تخمینی — با بنچمارک واقعی صنعت جایگزین شود]"},
            )
        LaborMarketStat.objects.get_or_create(
            period_label="مرداد ۱۴۰۵", job_role="تکنسین تعمیرگاه مجاز",
            defaults={"avg_industry_salary": 135000000, "turnover_rate": 18.0,
                      "source_name": "[نمونه]",
                      "analyst_note": "نرخ ترک شغل بالاتر این رده نسبت به کارشناس فروش، نشانه‌ی رقابت شدیدتر تعمیرگاه‌های آزاد برای جذب تکنسین ماهر است."},
        )

        # ===== ۹) مواد اولیه — چند دوره + مواد جدید =====
        steel_series = [("تیر ۱۴۰۵", 780000), ("مرداد ۱۴۰۵", 850000)]
        for period, price in steel_series:
            DomesticRawMaterial.objects.update_or_create(
                material_name="[نمونه] فولاد (ورق روغنی)", period_label=period,
                defaults={"usage_type": "ورق بدنه", "price": price, "unit": "کیلوگرم",
                          "monthly_fluctuation_pct": 9.0, "source_name": "[تخمینی]"},
            )
        DomesticRawMaterial.objects.get_or_create(
            material_name="پلیمر ABS", period_label="مرداد ۱۴۰۵",
            defaults={"usage_type": "داشبورد و قطعات پلاستیکی", "price": 620000, "unit": "کیلوگرم",
                      "monthly_fluctuation_pct": 4.5, "source_name": "[نمونه]"},
        )
        DomesticRawMaterial.objects.get_or_create(
            material_name="لاستیک خام (کائوچو)", period_label="مرداد ۱۴۰۵",
            defaults={"usage_type": "واشر و آب‌بندی", "price": 410000, "unit": "کیلوگرم",
                      "monthly_fluctuation_pct": 2.0, "source_name": "[نمونه]"},
        )
        DomesticRawMaterial.objects.get_or_create(
            material_name="رنگ صنعتی خودرو", period_label="مرداد ۱۴۰۵",
            defaults={"usage_type": "رنگ‌آمیزی بدنه", "price": 1250000, "unit": "کیلوگرم",
                      "monthly_fluctuation_pct": 6.5, "source_name": "[نمونه]",
                      "analyst_note": "قیمت رنگ صنعتی به‌دلیل وابستگی بالا به حلال‌های وارداتی، حساسیت زیادی به نرخ ارز دارد و در ماه‌های اخیر رشد بیش از میانگین صنعت داشته است."},
        )

        # ===== ۱۰) تسهیلات خودرو — چند دوره =====
        loan_series = [("تیر ۱۴۰۵", 22.0), ("مرداد ۱۴۰۵", 23.0)]
        for period, rate in loan_series:
            VehicleLoanRate.objects.update_or_create(
                period_label=period,
                defaults={"interest_rate": rate, "max_loan_amount": 800000000,
                          "mandatory_down_payment_pct": 30.0,
                          "source_name": "[تخمینی بر پایه‌ی نرخ عمومی تسهیلات بانکی]"},
            )

        # ===== ۱۱) واردات/صادرات — ۱ مورد دیگر =====
        VehiclePartsTradeStat.objects.get_or_create(
            period_label="تیر ۱۴۰۵",
            defaults={"imported_vehicle_count": 950, "parts_import_value": 42000000,
                      "parts_export_value": 4200000, "origin_destination": "چین (مبدأ عمده‌ی نمونه)",
                      "source_name": "نمونه — رقم واقعی از گمرک ایران باید ثبت شود"},
        )

        # ===== ۱۲) قطعات راهبردی — ۲ مورد دیگر =====
        StrategicElectronicPart.objects.get_or_create(
            part_name="سنسور اکسیژن (O2 Sensor)",
            defaults={"global_inventory_note": "موجودی جهانی نسبتاً پایدار، تولیدکنندگان متعدد.",
                      "delivery_time_days": 30, "price_usd": 45, "status": "normal", "source_name": "[نمونه]"},
        )
        StrategicElectronicPart.objects.get_or_create(
            part_name="ماژول کنترل ترمز ABS",
            defaults={"global_inventory_note": "کمبود جهانی چیپ‌های نیمه‌هادی مرتبط، تحویل با تأخیر قابل‌توجه.",
                      "delivery_time_days": 120, "price_usd": 210, "status": "critical", "source_name": "[نمونه]",
                      "analyst_note": "این قطعه در حال حاضر بحرانی‌ترین وضعیت تأمین را در سبد قطعات الکترونیک دارد؛ توصیه می‌شود موجودی احتیاطی حداقل برای تقاضای ۴ ماه آینده تأمین شود تا در صورت تشدید کمبود جهانی، خدمات تعمیرگاهی دچار وقفه نشود."},
        )

        # ===== ۱۳) گزارش تحلیلی دوره‌ای — ۱ گزارش دیگر برای دوره‌ی قبل =====
        MarketIntelReport.objects.get_or_create(
            title="گزارش تحلیلی هوش بازار — تیر ۱۴۰۵",
            defaults={
                "period_label": "تیر ۱۴۰۵", "report_date": datetime.date(2026, 7, 6),
                "summary": "نرخ ارز و تورم در مسیر صعودی قرار دارند؛ آمار تولید خودرو کشور نیز رشد ملایمی نشان می‌دهد.",
                "content": (
                    "در دوره‌ی تیرماه، نرخ دلار آزاد به ۱,۸۹۰,۰۰۰ ریال رسید که نسبت به خرداد ماه رشد محسوسی "
                    "داشت. تورم نقطه‌به‌نقطه نیز به ۸۳٪ رسید. در طرف مقابل، تولید خودرو کشور به ۷۱ هزار دستگاه "
                    "افزایش یافت که نشانه‌ی مثبتی برای تقاضای آتی قطعات یدکی است.\n\n"
                    "در حوزه‌ی تأمین داخلی، دو تأمین‌کننده‌ی جدید از استان‌های اصفهان و تهران شناسایی و به فهرست "
                    "تأمین‌کنندگان اضافه شدند که می‌تواند بخشی از وابستگی به واردات را در ماه‌های آینده کاهش دهد."
                ),
                "key_risks": "ادامه‌ی روند صعودی نرخ ارز و تورم؛ کمبود جهانی قطعات الکترونیک حساس.",
                "key_opportunities": "شناسایی تأمین‌کنندگان داخلی جدید در اصفهان و تهران.",
                "recommended_actions": "پیگیری قرارداد آزمایشی با تأمین‌کنندگان داخلی جدید؛ بررسی موجودی احتیاطی قطعات الکترونیک بحرانی.",
            },
        )

        self.stdout.write(self.style.SUCCESS("حجم داده‌ی نمونه‌ی هوش بازار به‌طور چشمگیر افزایش یافت."))
