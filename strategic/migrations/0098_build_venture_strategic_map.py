# -*- coding: utf-8 -*-
"""
بند ۳۰۰ — ساخت نقشه استراتژیک اولیه‌ی کسب‌وکار جدید «واسطه‌گری».

این پیش‌نویس نقشه (۶ محور، ۱۵ هدف در ۴ منظر BSC، با روابط علّی بین
هدف‌ها) بر اساس همون ۱۵ راهبرد TOWS که قبلاً وارد سامانه شد (بند ۲۹۹)
طراحی شده، و کاربر بعد از بررسی و اصلاح (اضافه‌شدن هدف C3 با تحلیل
کارشناسی) نسخه‌ی نهایی رو تأیید کرد.

نکته‌ی مهم: این هدف‌ها هنوز به هیچ شاخصی (KPI) وصل نیستن — چون این
کسب‌وکار هنوز شاخص کلان/عملیاتی تعریف‌شده‌ای نداره. تا وقتی کاربر
شاخص‌ها رو تعریف نکنه، روی نقشه به‌صورت «بدون شاخص وصل‌شده» دیده
می‌شن؛ این طبیعیه و بخشی از طراحی عمدیه.

این مهاجرت هم دقیقاً با همون الگوی امن بند ۲۹۹ نوشته شده:
  - قبل از هر کاری دنبال کسب‌وکاری با نام شامل «واسطه» می‌گرده. اگه
    دقیقاً یکی پیدا نشه، متوقف می‌شه و هیچ داده‌ای نمی‌نویسه.
  - idempotent هست: با get_or_create روی (کسب‌وکار، کد هدف) و
    (کسب‌وکار، نام محور)، اجرای دوباره هیچ موردی رو تکراری نمی‌سازه.
  - فقط داده اضافه می‌کنه، به هیچ کسب‌وکار یا هدف دیگه‌ای دست نمی‌زنه.
"""
import json

from django.db import migrations


DATA = json.loads(r"""
    {
        "themes": [
            "مدیریت عملیاتی",
            "مدیریت مشتری",
            "نوآوری",
            "مسئولیت‌های قانونی و اجتماعی",
            "سرمایه انسانی",
            "سرمایه سازمانی"
        ],
        "objectives": [
            [
                "F1",
                "financial",
                "مدیریت عملیاتی",
                "حداقل‌سازی کارمزد واسطه‌گری با بهره‌گیری از زیرساخت موجود",
                1
            ],
            [
                "F2",
                "financial",
                "مدیریت عملیاتی",
                "توسعه‌ی درآمد کارمزدی پایدار و کم‌ریسک در دوره‌های تورمی",
                2
            ],
            [
                "F3",
                "financial",
                "مدیریت عملیاتی",
                "تنوع‌بخشی به بخش‌های معاملاتی برای کاهش آسیب‌پذیری درآمد در رکود",
                3
            ],
            [
                "C1",
                "customer",
                "مدیریت مشتری",
                "ایجاد نقاط تحویل و تأیید فیزیکی امن در شبکه نمایندگی‌ها",
                1
            ],
            [
                "C2",
                "customer",
                "نوآوری",
                "تمرکز بر تنوع گسترده قطعات خودرو، به‌ویژه خودروهای از رده‌خارج",
                2
            ],
            [
                "C3",
                "customer",
                "مدیریت مشتری",
                "ایجاد و تثبیت اعتماد به‌عنوان واسطه‌ی بی‌طرف و قابل‌اطمینان بین خریدار و فروشنده",
                3
            ],
            [
                "P1",
                "process",
                "نوآوری",
                "جذب و تبدیل تأمین‌کنندگان و فروشندگان غیررسمی به شرکای رسمی شبکه",
                1
            ],
            [
                "P2",
                "process",
                "مدیریت عملیاتی",
                "طراحی و استقرار تدریجی فرایند اعتبارسنجی طرفین معامله، با الزام حداقلی احراز هویت در گام نخست",
                2
            ],
            [
                "P3",
                "process",
                "نوآوری",
                "طراحی سامانه مدیریت ریسک تقلب در معاملات واسطه‌ای",
                3
            ],
            [
                "P4",
                "process",
                "مسئولیت‌های قانونی و اجتماعی",
                "تدوین چارچوب حقوقی شفاف مسئولیت طرفین معامله",
                4
            ],
            [
                "P5",
                "process",
                "مدیریت عملیاتی",
                "خودکارسازی فرآیند مالی و مالیاتی معاملات کارمزدی",
                5
            ],
            [
                "P6",
                "process",
                "نوآوری",
                "راه‌اندازی آزمایشی و کنترل‌شده (Pilot) پیش از ورود گسترده به بازار",
                6
            ],
            [
                "L1",
                "learning",
                "سرمایه سازمانی",
                "تثبیت جایگاه سازمانی و مرز مسئولیت واحد، پیش از توسعه مقیاس",
                1
            ],
            [
                "L2",
                "learning",
                "سرمایه انسانی",
                "وام‌گیری و انتقال دانش عملیاتی از کسب‌وکارهای بازرگانی قطعات و آپشن",
                2
            ],
            [
                "L3",
                "learning",
                "سرمایه سازمانی",
                "محدودسازی هدفمند دامنه فعالیت تا بلوغ کافی تجربه عملیاتی",
                3
            ]
        ],
        "feeds": {
            "L1": [
                "P2",
                "P4"
            ],
            "L2": [
                "P1",
                "P5"
            ],
            "L3": [
                "P6"
            ],
            "P1": [
                "C2"
            ],
            "P2": [
                "C3"
            ],
            "P3": [
                "C3"
            ],
            "P4": [
                "C3"
            ],
            "P5": [
                "F1"
            ],
            "P6": [
                "F2"
            ],
            "C1": [
                "F3"
            ],
            "C2": [
                "F2"
            ],
            "C3": [
                "F1",
                "F3"
            ]
        }
    }
""")


def build_venture_map(apps, schema_editor):
    BusinessUnit = apps.get_model("strategic", "BusinessUnit")
    StrategyTheme = apps.get_model("strategic", "StrategyTheme")
    StrategicObjective = apps.get_model("strategic", "StrategicObjective")

    candidates = list(BusinessUnit.objects.filter(name__icontains="واسطه"))
    if len(candidates) != 1:
        names = ", ".join(b.name for b in candidates) or "(هیچ‌کدام)"
        raise RuntimeError(
            "مهاجرت بند ۳۰۰ متوقف شد: کسب‌وکار «واسطه‌گری» به‌صورت دقیق "
            f"پیدا نشد (کاندیداهای یافت‌شده: {names}). لطفاً مطمئن شوید "
            "دقیقاً یک کسب‌وکار با نامی شامل «واسطه» توی سامانه هست، بعد "
            "دوباره «python manage.py migrate strategic» را اجرا کنید. "
            "تا وقتی این مشکل حل نشه، هیچ داده‌ای نوشته نمی‌شه."
        )
    bu = candidates[0]

    # قدم ۱: ساخت محورهای استراتژیک (ستون‌های نقشه) این کسب‌وکار.
    theme_objs = {}
    for order, name in enumerate(DATA["themes"], start=1):
        theme, _ = StrategyTheme.objects.get_or_create(
            business_unit=bu, name=name, defaults={"order": order},
        )
        theme_objs[name] = theme

    # قدم ۲: ساخت هدف‌های استراتژیک (کارت‌های نقشه)، هر کدام با محور
    # و منظر خودش، و نگه‌داشتن نگاشت کد <-> شیء برای وصل کردن روابط
    # علّی در قدم بعد.
    code_to_obj = {}
    for code, perspective, theme_name, title, order in DATA["objectives"]:
        obj, _ = StrategicObjective.objects.get_or_create(
            business_unit=bu,
            code=code,
            defaults={
                "perspective": perspective,
                "theme": theme_objs[theme_name],
                "title": title,
                "order": order,
            },
        )
        code_to_obj[code] = obj

    # قدم ۳: وصل کردن روابط علّی (این هدف به کدام هدف‌ها کمک می‌کند).
    for from_code, to_codes in DATA["feeds"].items():
        from_obj = code_to_obj.get(from_code)
        if not from_obj:
            continue
        targets = [code_to_obj[c] for c in to_codes if c in code_to_obj]
        if targets:
            from_obj.feeds_into.set(targets)

    print(
        f"\n[بند ۳۰۰] کسب‌وکار «{bu.name}» — "
        f"{len(theme_objs)} محور و {len(code_to_obj)} هدف استراتژیک "
        "(با روابط علّی) ثبت شد (موارد تکراری رد شدند)."
    )


def remove_venture_map(apps, schema_editor):
    """برگرداندن این مهاجرت: فقط همون هدف‌ها و محورهایی که خودمون با
    همین کدها/نام‌ها ساختیم حذف می‌شه، به بقیه‌ی داده‌های سامانه دست
    نمی‌زنه."""
    BusinessUnit = apps.get_model("strategic", "BusinessUnit")
    StrategyTheme = apps.get_model("strategic", "StrategyTheme")
    StrategicObjective = apps.get_model("strategic", "StrategicObjective")

    candidates = list(BusinessUnit.objects.filter(name__icontains="واسطه"))
    if len(candidates) != 1:
        return
    bu = candidates[0]

    codes = [o[0] for o in DATA["objectives"]]
    StrategicObjective.objects.filter(business_unit=bu, code__in=codes).delete()
    StrategyTheme.objects.filter(business_unit=bu, name__in=DATA["themes"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0097_import_venture_swot_data"),
    ]

    operations = [
        migrations.RunPython(build_venture_map, remove_venture_map),
    ]
