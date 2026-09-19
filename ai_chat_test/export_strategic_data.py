#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ابزار تست چت‌بات هوش مصنوعی — قدم ۱: استخراج داده‌ها از سامانه
=================================================================

این فایل کاملاً جداگانه و مستقل است — هیچ فایل دیگری از سامانه‌ی اصلی
رو تغییر نمی‌ده و به هیچ فایلی وابسته نیست به‌جز اینکه از مدل‌های
موجود سامانه (فقط برای خواندن اطلاعات) استفاده می‌کنه.

اگه هر زمانی خواستید این آزمایش رو کنار بذارید، کافیه کل پوشه‌ی
"ai_chat_test" رو پاک کنید — هیچ اثری روی بقیه‌ی سامانه نمی‌ذاره.

این اسکریپت چیکار می‌کنه:
  ۱) به دیتابیس واقعی سامانه (db.sqlite3) وصل می‌شه — فقط می‌خونه، هیچی
     رو تغییر نمی‌ده یا نمی‌نویسه.
  ۲) اطلاعات نقشه‌ی استراتژیک (اهداف، شاخص‌ها، وزن‌ها، درصد تحقق و
     وضعیت محاسبه‌شده‌ی هر کارت) رو برای همه‌ی کسب‌وکارها جمع می‌کنه —
     دقیقاً با همون منطق محاسبه‌ای که خود سامانه استفاده می‌کنه (چون
     از همون تابع محاسبه‌ی خود سامانه استفاده می‌کنه، نه یه محاسبه‌ی
     جداگانه و احتمالاً اشتباه).
  ۳) همه‌ی این اطلاعات رو توی یه فایل ساده‌ی JSON با اسم
     "strategic_export.json" (کنار همین فایل) ذخیره می‌کنه.

نحوه‌ی اجرا (از پوشه‌ی اصلی پروژه، همونجایی که manage.py هست):

    python ai_chat_test\\export_strategic_data.py

بعد از اجرا، یه فایل به اسم strategic_export.json توی همین پوشه
(ai_chat_test) ساخته می‌شه. این فایل رو مرحله‌ی بعدی (چت‌بات) می‌خونه.

نکته: اگه خواستید داده‌ها رو دوباره تازه کنید (بعد از اینکه اطلاعات
سامانه عوض شد)، کافیه همین اسکریپت رو دوباره اجرا کنید.
"""

import os
import sys
import json
import datetime

# ---------------------------------------------------------------------------
# قدم ۱: وصل شدن به تنظیمات جنگو سامانه‌ی اصلی (فقط برای خواندن اطلاعات)
# ---------------------------------------------------------------------------
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(THIS_DIR)  # یک پوشه بالاتر از ai_chat_test
sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402
django.setup()

# این ایمپورت‌ها فقط برای «خواندن» اطلاعات هستن — هیچ‌جای این اسکریپت
# چیزی save/create/update/delete نمی‌شه.
from strategic.models import BusinessUnit, StrategicObjective  # noqa: E402
from strategic.views import _attach_computed_objective_status  # noqa: E402

PERSPECTIVE_LABEL = {
    "financial": "مالی",
    "customer": "مشتری",
    "process": "فرآیندهای داخلی",
    "learning": "یادگیری و رشد",
}


def build_objective_dict(o):
    """یه دیکشنری ساده و خوانا از یک کارت هدف استراتژیک می‌سازه."""
    kpi_list = []
    for k in o.linked_kpis.all():
        w = next((ww.weight for ww in o.objectivekpiweight_set.all() if ww.kpi_id == k.pk), 100) \
            if hasattr(o, "objectivekpiweight_set") else 100
        kpi_list.append({
            "نوع": "کلان",
            "کد": k.code,
            "نام": k.name,
            "درصد_تحقق": k.manual_progress_value,
            "وزن": w,
        })
    for k in o.linked_operational_kpis.all():
        w = next((ww.weight for ww in o.objectiveoperationalkpiweight_set.all() if ww.kpi_id == k.pk), 100) \
            if hasattr(o, "objectiveoperationalkpiweight_set") else 100
        kpi_list.append({
            "نوع": "عملیاتی",
            "کد": k.code,
            "نام": k.title,
            "درصد_تحقق": k.manual_progress_value,
            "وزن": w,
        })
    return {
        "کد": o.code,
        "عنوان": o.title,
        "منظر": PERSPECTIVE_LABEL.get(o.perspective, o.perspective),
        "درصد_تحقق_کارت": getattr(o, "computed_pct", None),
        "وضعیت_کارت": getattr(o, "computed_status_label", None) or "بدون شاخص وصل‌شده",
        "شاخص‌ها": kpi_list,
    }


def main():
    export = {
        "تاریخ_تولید": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "کسب‌وکارها": [],
    }

    business_units = list(BusinessUnit.objects.all())
    for bu in business_units:
        objectives = list(
            StrategicObjective.objects
            .filter(business_unit=bu)
            .prefetch_related("linked_kpis", "linked_operational_kpis")
        )
        # همون تابعی که خود سامانه برای محاسبه‌ی وضعیت هر کارت استفاده
        # می‌کنه — تا عددها دقیقاً با چیزی که مدیر روی صفحه می‌بینه یکی باشه.
        _attach_computed_objective_status(objectives)

        on = sum(1 for o in objectives if getattr(o, "computed_status", None) == "on")
        watch = sum(1 for o in objectives if getattr(o, "computed_status", None) == "watch")
        risk = sum(1 for o in objectives if getattr(o, "computed_status", None) == "risk")
        no_data = sum(1 for o in objectives if getattr(o, "computed_status", None) is None)

        export["کسب‌وکارها"].append({
            "شناسه": bu.pk,
            "نام": bu.name,
            "خلاصه": {
                "تعداد_کل_اهداف": len(objectives),
                "در_مسیر": on,
                "نیازمند_پیگیری": watch,
                "در_معرض_ریسک": risk,
                "بدون_شاخص": no_data,
            },
            "اهداف": [build_objective_dict(o) for o in objectives],
        })

    out_path = os.path.join(THIS_DIR, "strategic_export.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(export, f, ensure_ascii=False, indent=2)

    print("انجام شد.")
    print("فایل ساخته شد:", out_path)
    for bu in export["کسب‌وکارها"]:
        s = bu["خلاصه"]
        print(f"  - {bu['نام']}: {s['تعداد_کل_اهداف']} هدف "
              f"(در مسیر: {s['در_مسیر']}, نیازمند پیگیری: {s['نیازمند_پیگیری']}, "
              f"در معرض ریسک: {s['در_معرض_ریسک']}, بدون شاخص: {s['بدون_شاخص']})")


if __name__ == "__main__":
    main()
