"""بازطراحی کارت‌های نقشه‌ی استراتژیک «واسطه‌گری» (۲۳ کارت نتیجه‌محور).

استفاده:
    python manage.py rebuild_brokerage_map            # فقط گزارش (بدون تغییر)
    python manage.py rebuild_brokerage_map --apply    # اعمال تغییرات

قبل از --apply حتماً از db.sqlite3 نسخه‌ی پشتیبان بگیرید.
اقدامات: حذف کارت‌های فعلی این کسب‌وکار و ساخت ۲۳ کارت جدید با پیوندهای علّی،
راهبرد TOWS مبنا، شاخص‌ها و استراتژی‌های وظیفه‌ای مرتبط.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from strategic.models import (
    BusinessUnit, StrategicObjective, StrategyTheme, TOWSStrategy, FunctionalStrategy,
    CompanyKPI, OperationalKPI, ObjectiveKPIWeight, ObjectiveOperationalKPIWeight,
)

BU_NAME = "واسطه گری"

# (code, perspective, title, theme, tows_id)
CARDS = [
    ("F1", "financial", "سود عملیاتی واسطه‌گری", "مدیریت عملیاتی", None),
    ("F2", "financial", "بهره‌وری هزینه با زیرساخت موجود", "مدیریت عملیاتی", 101),
    ("F3", "financial", "رشد درآمد کارمزدی", "مدیریت مشتری", 103),
    ("F4", "financial", "پایداری درآمد در رکود", "مدیریت مشتری", 111),
    ("F5", "financial", "کاهش زیان تقلب و ریسک حقوقی", "مدیریت عملیاتی", None),
    ("C1", "customer", "اعتماد به واسطه‌ی بی‌طرف", "مدیریت مشتری", 114),
    ("C2", "customer", "تنوع قطعات (از جمله خودروهای از رده‌خارج)", "نوآوری", 108),
    ("C3", "customer", "امنیت تحویل و تسویه", "مدیریت مشتری", 104),
    ("C4", "customer", "رشد فروشندگان رسمی", "مدیریت مشتری", None),
    ("C5", "customer", "رشد و وفاداری خریداران", "مدیریت مشتری", None),
    ("P1", "process", "اعتبارسنجی طرفین معامله", "مدیریت عملیاتی", 105),
    ("P2", "process", "مدیریت ریسک تقلب", "مسئولیت‌های قانونی و اجتماعی", 107),
    ("P3", "process", "چارچوب حقوقی مسئولیت معامله", "مسئولیت‌های قانونی و اجتماعی", 109),
    ("P4", "process", "عملیات مالی و مالیاتی کارمزد", "مدیریت عملیاتی", 110),
    ("P5", "process", "تحویل، بازرسی و مرجوعی در شبکه نمایندگی", "مدیریت عملیاتی", None),
    ("P6", "process", "جذب و رسمی‌سازی فروشندگان", "مدیریت مشتری", 102),
    ("P7", "process", "نگهداشت و تحلیل رفتار خریداران", "مدیریت مشتری", None),
    ("P8", "process", "توسعه تنوع اقلام و نیچ بازار", "نوآوری", None),
    ("P9", "process", "ورود مرحله‌ای و کنترل‌شده (Pilot)", "نوآوری", 113),
    ("L1", "learning", "پلتفرم و داده‌ی معاملات", "سرمایه اطلاعاتی", None),
    ("L2", "learning", "دانش و مهارت واسطه‌گری و ریسک", "سرمایه انسانی", 106),
    ("L3", "learning", "شفافیت جایگاه و مسئولیت سازمانی", "سرمایه سازمانی", 112),
    ("L4", "learning", "مدیریت دانش تجربه‌ی عملیاتی", "سرمایه اطلاعاتی", 115),
]

# پیکان‌ها: از ← به
FEEDS = {
    "F2": ["F1"], "F3": ["F1"], "F4": ["F1"], "F5": ["F1"],
    "C1": ["F3", "F5"], "C2": ["F3", "F4"], "C3": ["F3"], "C4": ["F3", "F4"], "C5": ["F3"],
    "P1": ["C1"], "P2": ["C1", "F5"], "P3": ["C1", "F5"], "P4": ["F2"], "P5": ["C3"],
    "P6": ["C4"], "P7": ["C5"], "P8": ["C2"], "P9": ["F5", "C1"],
    "L1": ["P1", "P2", "P4", "P7"], "L2": ["P1", "P2", "P6", "P8"],
    "L3": ["P3", "P5"], "L4": ["P9", "P1"],
}

# شاخص‌ها: کد کارت ← (کد شاخص کلان | None، کد شاخص عملیاتی | None)
COMPANY_KPIS = {"F3": ["I23"]}
OPERATIONAL_KPIS = {"F3": ["C-01-33"], "C2": ["C-01-60"], "C4": ["C-01-40"], "C5": ["C-01-61"]}

# استراتژی‌های وظیفه‌ای: (شناسه، ابتدای عنوان برای اطمینان) ← کارت‌ها
FS_LINKS = [
    (9, "خودکارسازی فرآیندهای مالی", ["P4"]),
    (125, "جذب و توسعه شبکه فروشندگان", ["P6", "C4"]),
    (126, "افزایش تنوع اقلام قابل ارائه", ["P8", "C2"]),
    (127, "افزایش تعداد خریداران", ["P7", "C5"]),
]
THEME_ORDER = ["مدیریت عملیاتی", "مدیریت مشتری", "نوآوری", "مسئولیت‌های قانونی و اجتماعی",
               "سرمایه انسانی", "سرمایه اطلاعاتی", "سرمایه سازمانی"]


def _norm(s):
    return (s or "").replace("ي", "ی").replace("ك", "ک").replace("‌", "").replace(" ", "")


class Command(BaseCommand):
    help = "بازطراحی کارت‌های نقشه‌ی استراتژیک کسب‌وکار واسطه‌گری (پیش‌فرض: فقط گزارش)"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="تغییرات را واقعاً اعمال کن")

    def handle(self, *args, **opts):
        bu = BusinessUnit.objects.filter(name__contains="واسطه").first()
        if not bu:
            raise CommandError("کسب‌وکار «واسطه گری» پیدا نشد.")
        old = StrategicObjective.objects.filter(business_unit=bu)
        self.stdout.write(f"کسب‌وکار: {bu.name} — کارت‌های فعلی: {old.count()} ← کارت‌های جدید: {len(CARDS)}")

        plan_issues = []
        for fs_id, prefix, _ in FS_LINKS:
            fs = FunctionalStrategy.objects.filter(pk=fs_id).first()
            if not fs or not _norm(fs.title).startswith(_norm(prefix)):
                plan_issues.append(f"استراتژی وظیفه‌ای {fs_id} با عنوان مورد انتظار نیست؛ لینک نمی‌شود.")
        tows_ids = {t for *_, t in CARDS if t}
        found = set(TOWSStrategy.objects.filter(pk__in=tows_ids, business_unit=bu).values_list("pk", flat=True))
        for t in sorted(tows_ids - found):
            plan_issues.append(f"راهبرد TOWS شماره {t} در این کسب‌وکار نیست؛ مبنا خالی می‌ماند.")
        for k in ("I23",):
            if not CompanyKPI.objects.filter(code=k).exists():
                plan_issues.append(f"شاخص کلان {k} نیست.")
        for codes in OPERATIONAL_KPIS.values():
            for k in codes:
                if not OperationalKPI.objects.filter(code=k).exists():
                    plan_issues.append(f"شاخص عملیاتی {k} نیست.")
        for p in plan_issues:
            self.stdout.write(self.style.WARNING("هشدار: " + p))

        if not opts["apply"]:
            self.stdout.write("حالت گزارش: چیزی تغییر نکرد. برای اعمال، --apply را اضافه کنید (قبلش پشتیبان بگیرید).")
            return

        with transaction.atomic():
            old.delete()  # وزن شاخص‌ها، پیکان‌ها و لینک استراتژی وظیفه‌ای مرتبط هم پاک می‌شود

            themes = {}
            existing = {t.name: t for t in StrategyTheme.objects.filter(business_unit=bu)}
            for i, name in enumerate(THEME_ORDER, start=1):
                t = existing.get(name) or StrategyTheme(business_unit=bu, name=name)
                t.order = i
                t.save()
                themes[name] = t

            objs, order_by_persp = {}, {}
            for code, persp, title, theme, tows_id in CARDS:
                order_by_persp[persp] = order_by_persp.get(persp, 0) + 1
                objs[code] = StrategicObjective.objects.create(
                    code=code, perspective=persp, title=title, theme=themes[theme], status="on",
                    order=order_by_persp[persp], business_unit=bu,
                    source_tows_id=tows_id if tows_id in found else None,
                )
            for src, targets in FEEDS.items():
                objs[src].feeds_into.set([objs[t] for t in targets])

            for code, kpis in COMPANY_KPIS.items():
                for k in kpis:
                    kobj = CompanyKPI.objects.filter(code=k).first()
                    if kobj:
                        ObjectiveKPIWeight.objects.create(objective=objs[code], kpi=kobj, weight=100)
            for code, kpis in OPERATIONAL_KPIS.items():
                for k in kpis:
                    kobj = OperationalKPI.objects.filter(code=k).first()
                    if kobj:
                        ObjectiveOperationalKPIWeight.objects.create(objective=objs[code], kpi=kobj, weight=100)

            linked = 0
            for fs_id, prefix, codes in FS_LINKS:
                fs = FunctionalStrategy.objects.filter(pk=fs_id).first()
                if fs and _norm(fs.title).startswith(_norm(prefix)):
                    fs.linked_objectives.add(*[objs[c] for c in codes])
                    linked += 1

        self.stdout.write(self.style.SUCCESS(
            f"انجام شد: {len(CARDS)} کارت، {sum(len(v) for v in FEEDS.values())} پیکان، "
            f"{linked} استراتژی وظیفه‌ای لینک شد."))
