"""بازطراحی نقشه‌ی استراتژیک «واسطه‌گری» در فضای «برتری عملیاتی» (۲۹ کارت).

الگو: نقشه‌ی استراتژی برتری عملیاتی (ارزش بلندمدت سهام‌دار ← بهره‌وری و رشد؛ ارزش‌پیشنهادی: قیمت پایین،
کیفیت، سهولت و انتخاب؛ فرایندهای مدیریت عملیاتی / مشتری / نوآوری / قانونی و اجتماعی؛ سه سرمایه‌ی یادگیری و رشد)
مبنا: ۱۵ راهبرد TOWS و ۴ استراتژی وظیفه‌ای واسطه‌گری.

    python manage.py rebuild_brokerage_map_excellence            # فقط گزارش (بدون تغییر)
    python manage.py rebuild_brokerage_map_excellence --apply    # اعمال

• پیش از اعمال، پشتیبان کامل نقشه‌ی فعلی در پوشه‌ی backups/ ذخیره می‌شود؛ بازگشت:
    python manage.py restore_brokerage_map --file backups/<فایل>.json --apply
• لینک پروژه‌ها، ریسک‌ها، شاخص‌های هدف و استراتژی‌های وظیفه‌ای کارت‌های قبلی، طبق نگاشت OLD_TO_NEW به کارت جدید منتقل می‌شود.
• رویکرد کسب‌وکار از «فضای انحصاری» به «برتری عملیاتی» تغییر می‌کند.
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from strategic.models import (
    BusinessUnit, StrategicObjective, StrategyTheme, TOWSStrategy, FunctionalStrategy, CompanyKPI,
    OperationalKPI, ObjectiveKPIWeight, ObjectiveOperationalKPIWeight, Risk, StrategicKPI,
)
from ._bmap_io import save_snapshot

OP, CUS, INN, LEG = "مدیریت عملیاتی", "مدیریت مشتری", "نوآوری", "مسئولیت‌های قانونی و اجتماعی"
HUM, INF, ORG = "سرمایه انسانی", "سرمایه اطلاعاتی", "سرمایه سازمانی"
THEME_ORDER = [OP, CUS, INN, LEG, HUM, INF, ORG]

# (کد، منظر، محور، عنوان، شماره‌ی راهبرد TOWS مبنا، پیکان‌ها ←، توضیح مبنا)
CARDS = [
    # ── مالی ──
    ("F1", "financial", OP, "سود عملیاتی واسطه‌گری (ارزش بلندمدت سهام‌دار)", None, [], "هدف نهایی نقشه"),
    ("F2", "financial", OP, "استراتژی بهره‌وری", None, ["F1"], "الگوی برتری عملیاتی"),
    ("F3", "financial", CUS, "استراتژی رشد", None, ["F1"], "الگوی برتری عملیاتی"),
    ("F4", "financial", OP, "بهبود ساختار هزینه با سربار حداقلی", None, ["F2"], "S1،S2 — کسب‌وکار کم‌سرمایه و بدون موجودی"),
    ("F5", "financial", OP, "افزایش کاربری از دارایی‌های موجود (پلتفرم، بانک اطلاعات، شبکه‌ی نمایندگی)", None, ["F2"], "S2،S3،S5"),
    ("F6", "financial", CUS, "توسعه فرصت‌های درآمدی کارمزدی کم‌ریسک", 103, ["F3"], "SO3 — O3"),
    ("F7", "financial", CUS, "تقویت ارزش مشتری (افزایش خریداران و فروشندگان فعال)", None, ["F3"], "استراتژی وظیفه‌ای ۱۲۷ و ۱۲۵"),
    # ── مشتری (ارزش‌پیشنهادی: خرید با کمترین هزینه‌ی نهایی، کیفیت مطمئن و سهولت) ──
    ("C1", "customer", INN, "انتخاب مناسب: تنوع قطعات برای همه‌ی خودروها (از جمله از رده‌خارج)", 111, ["F6", "F7"], "ST3 — تنوع‌بخشی؛ استراتژی وظیفه‌ای ۱۲۶"),
    ("C2", "customer", CUS, "خرید سریع و آسان", None, ["F7"], "O2 — رشد خرید آنلاین"),
    ("C3", "customer", OP, "کیفیت عالی: معامله‌ی امن با طرف معتبر", 114, ["F6", "F7"], "WT3 — احراز هویت پیش از معامله"),
    ("C4", "customer", OP, "قیمت رقابتی و کارمزد حداقلی", 101, ["F7"], "SO1 — سربار پایین"),
    # ── فرایندهای داخلی ──
    ("P1", "process", OP, "جذب و رسمی‌سازی فروشندگان و تأمین‌کنندگان معتبر", 102, ["C1", "C4", "F5"], "SO2؛ استراتژی وظیفه‌ای ۱۲۵"),
    ("P2", "process", OP, "اعتبارسنجی و احراز هویت طرفین معامله", 105, ["C3"], "WO1 — W2"),
    ("P3", "process", OP, "خودکارسازی صدور فاکتور، مالیات و تسویه‌ی معاملات", 110, ["F4", "C2"], "ST2 — T5؛ استراتژی وظیفه‌ای ۹"),
    ("P4", "process", OP, "تحویل، بازرسی و مرجوعی از طریق شبکه‌ی نمایندگی‌ها", 104, ["C3", "C2", "F5"], "SO4 — S5"),
    ("P5", "process", OP, "مدیریت ریسک تقلب و اعتبار معاملات", 107, ["C3", "F4"], "WO3 — W4"),
    ("P6", "process", CUS, "بازاریابی دیجیتال و جذب خریداران (داده‌محور)", None, ["C2", "F7"], "استراتژی وظیفه‌ای ۱۲۸"),
    ("P7", "process", CUS, "نگهداشت، وفادارسازی و تحلیل رفتار خریداران", None, ["F7", "C2"], "استراتژی وظیفه‌ای ۱۲۷"),
    ("P8", "process", CUS, "پاسخگویی سریع به سفارش (از ثبت تا تحویل)", None, ["C2"], "الگوی برتری عملیاتی"),
    ("P9", "process", CUS, "تدارک قطعات موردنیاز مشتری (تنوع اقلام و خودروهای از رده‌خارج)", 108, ["C1"], "WO4؛ استراتژی وظیفه‌ای ۱۲۶"),
    ("P10", "process", INN, "ورود مرحله‌ای و کنترل‌شده (Pilot) روش‌های فروش و گروه‌های قطعه", 113, ["P9", "P5"], "WT2 — W4،W5"),
    ("P11", "process", INN, "پایش عملکرد و ارزیابی رقبا (پلتفرم‌های آنلاین مستقل)", None, ["C4", "P9"], "T2؛ استراتژی وظیفه‌ای ۱۲۶"),
    ("P12", "process", LEG, "چارچوب حقوقی و قراردادی مسئولیت طرفین معامله", 109, ["C3", "P5"], "ST1 — T1،T3"),
    ("P13", "process", LEG, "صیانت از اعتبار برند و ساماندهی بازار غیررسمی و قطعه‌ی تقلبی", None, ["C3"], "T3، O5"),
    # ── یادگیری و رشد ──
    ("L1", "learning", HUM, "دانش و مهارت واسطه‌گری، ارزیابی ریسک و پاسخگویی به مشتری", 106, ["P2", "P5", "P6", "P7"], "WO2 — W1"),
    ("L2", "learning", INF, "یکپارچگی الکترونیکی با فروشندگان و خریداران (پلتفرم و بانک اطلاعات)", None, ["P1", "P3", "P6", "P8"], "S2،S3"),
    ("L3", "learning", INF, "مدیریت دانش و تحلیل داده‌ی تجربه‌ی عملیاتی", 115, ["P10", "P11", "P7"], "WT4 — W1"),
    ("L4", "learning", ORG, "شفافیت جایگاه و مسئولیت سازمانی واحد واسطه‌گری", 112, ["P12", "P4"], "WT1 — W3"),
    ("L5", "learning", ORG, "تسهیم دانش و بهبود مستمر فرایندها (بهتر، سریع‌تر، ارزان‌تر)", None, ["P3", "P8", "P11"], "الگوی برتری عملیاتی"),
]

# شاخص‌ها: کد کارت ← ([شاخص کلان], [شاخص عملیاتی])
KPIS = {
    "F6": (["I23"], ["C-01-33"]),
    "F7": ([], ["C-01-61"]),
    "C1": ([], ["C-01-60"]),
    "P1": ([], ["C-01-40"]),
}

# استراتژی‌های وظیفه‌ای: (شناسه، ابتدای عنوان برای اطمینان) ← کارت‌ها
FS_LINKS = [
    (9, "خودکارسازی فرآیندهای مالی", ["P3", "F4"]),
    (125, "جذب و توسعه شبکه فروشندگان", ["P1", "F5"]),
    (126, "افزایش تنوع اقلام قابل ارائه", ["P9", "P11", "C1"]),
    (127, "افزایش تعداد خریداران", ["P7", "F7"]),
    (128, "طراحی و اجرای کمپین", ["P6", "F7"]),
]

# نگاشت کارت‌های نقشه‌ی قبلی (۲۳ کارت) ← کارت جدید؛ برای انتقال پروژه‌ها، ریسک‌ها و شاخص‌های هدف
OLD_TO_NEW = {
    "F1": "F1", "F2": "F4", "F3": "F6", "F4": "F6", "F5": "P5",
    "C1": "C3", "C2": "C1", "C3": "C3", "C4": "P1", "C5": "F7",
    "P1": "P2", "P2": "P5", "P3": "P12", "P4": "P3", "P5": "P4", "P6": "P1", "P7": "P7", "P8": "P9", "P9": "P10",
    "L1": "L2", "L2": "L1", "L3": "L4", "L4": "L3",
}


def _norm(s):
    return (s or "").replace("ي", "ی").replace("ك", "ک").replace("‌", "").replace(" ", "")


class Command(BaseCommand):
    help = "بازطراحی نقشه‌ی واسطه‌گری در فضای برتری عملیاتی (پیش‌فرض: فقط گزارش)"

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true", help="تغییرات را واقعاً اعمال کن")

    def handle(self, *args, **opts):
        bu = BusinessUnit.objects.filter(name__contains="واسطه").first()
        if not bu:
            raise CommandError("کسب‌وکار «واسطه گری» پیدا نشد.")
        old = list(StrategicObjective.objects.filter(business_unit=bu))
        codes = [c[0] for c in CARDS]
        assert len(codes) == len(set(codes))
        for c in CARDS:
            for t in c[5]:
                assert t in codes, f"پیکان نامعتبر {c[0]}→{t}"
        self.stdout.write(f"کسب‌وکار: {bu.name} (رویکرد فعلی: {bu.get_archetype_display()}) — "
                          f"کارت‌های فعلی: {len(old)} ← کارت‌های جدید: {len(CARDS)}")

        issues = []
        tows_ids = {c[4] for c in CARDS if c[4]}
        found = set(TOWSStrategy.objects.filter(pk__in=tows_ids, business_unit=bu).values_list("pk", flat=True))
        for t in sorted(tows_ids - found):
            issues.append(f"راهبرد TOWS شماره {t} در این کسب‌وکار نیست؛ مبنای کارت خالی می‌ماند.")
        for fs_id, prefix, _ in FS_LINKS:
            fs = FunctionalStrategy.objects.filter(pk=fs_id).first()
            if not fs or not _norm(fs.title).startswith(_norm(prefix)):
                issues.append(f"استراتژی وظیفه‌ای {fs_id} با عنوان مورد انتظار نیست؛ لینک نمی‌شود.")
        for ck, ok in KPIS.values():
            for k in ck:
                if not CompanyKPI.objects.filter(code=k).exists():
                    issues.append(f"شاخص کلان {k} نیست.")
            for k in ok:
                if not OperationalKPI.objects.filter(code=k).exists():
                    issues.append(f"شاخص عملیاتی {k} نیست.")
        # لینک‌هایی که منتقل می‌شوند
        move_ini = move_risk = move_kpi = move_fs = 0
        for o in old:
            if o.code not in OLD_TO_NEW:
                if o.initiatives.exists() or Risk.objects.filter(linked_objective=o).exists():
                    issues.append(f"کارت قدیمی {o.code} در نگاشت نیست؛ لینک‌های آن از بین می‌رود.")
                continue
            move_ini += o.initiatives.count()
            move_risk += Risk.objects.filter(linked_objective=o).count()
            move_kpi += StrategicKPI.objects.filter(objective=o).count()
            move_fs += o.functional_strategies.count()
        for p in issues:
            self.stdout.write(self.style.WARNING("هشدار: " + p))
        self.stdout.write(f"لینک‌هایی که به کارت جدید منتقل می‌شود: پروژه {move_ini}، ریسک {move_risk}، "
                          f"شاخص هدف {move_kpi}، استراتژی وظیفه‌ای {move_fs}")
        self.stdout.write("")
        for code, persp, theme, title, tows, feeds, basis in CARDS:
            self.stdout.write(f"{code:<4}[{theme}] {title}   ←مبنا: {basis}" + (f" | TOWS {tows}" if tows else ""))

        if not opts["apply"]:
            self.stdout.write("\nحالت گزارش: چیزی تغییر نکرد. برای اعمال، --apply را اضافه کنید.")
            return

        path, _ = save_snapshot(bu)
        self.stdout.write(self.style.SUCCESS(f"پشتیبان نقشه‌ی فعلی ذخیره شد: {path}"))

        with transaction.atomic():
            themes = {}
            existing = {t.name: t for t in StrategyTheme.objects.filter(business_unit=bu)}
            for i, name in enumerate(THEME_ORDER, start=1):
                t = existing.get(name) or StrategyTheme(business_unit=bu, name=name)
                t.order = i
                t.save()
                themes[name] = t

            objs, per = {}, {}
            for code, persp, theme, title, tows, feeds, basis in CARDS:
                per[persp] = per.get(persp, 0) + 1
                objs[code] = StrategicObjective.objects.create(
                    code=code, perspective=persp, title=title, theme=themes[theme], status="on",
                    order=per[persp], business_unit=bu, source_tows_id=tows if tows in found else None,
                )
            for code, *_r in CARDS:
                objs[code].feeds_into.set([objs[t] for t in _r[4]])

            for code, (ck, ok) in KPIS.items():
                for k in ck:
                    kobj = CompanyKPI.objects.filter(code=k).first()
                    if kobj:
                        ObjectiveKPIWeight.objects.create(objective=objs[code], kpi=kobj, weight=100)
                for k in ok:
                    kobj = OperationalKPI.objects.filter(code=k).first()
                    if kobj:
                        ObjectiveOperationalKPIWeight.objects.create(objective=objs[code], kpi=kobj, weight=100)

            # انتقال لینک‌های کارت‌های قبلی
            for o in old:
                new = objs.get(OLD_TO_NEW.get(o.code, ""))
                if not new:
                    continue
                for ini in o.initiatives.all():
                    ini.objectives.add(new)
                Risk.objects.filter(linked_objective=o).update(linked_objective=new)
                StrategicKPI.objects.filter(objective=o).update(objective=new)
                for fs in o.functional_strategies.all():
                    fs.linked_objectives.add(new)
            StrategicObjective.objects.filter(pk__in=[o.pk for o in old]).delete()

            linked = 0
            for fs_id, prefix, cs in FS_LINKS:
                fs = FunctionalStrategy.objects.filter(pk=fs_id).first()
                if fs and _norm(fs.title).startswith(_norm(prefix)):
                    fs.linked_objectives.add(*[objs[c] for c in cs])
                    linked += 1

            bu.archetype = "excellence"
            bu.save()

        self.stdout.write(self.style.SUCCESS(
            f"انجام شد: {len(CARDS)} کارت، {sum(len(c[5]) for c in CARDS)} پیکان، {linked} استراتژی وظیفه‌ای لینک شد؛ "
            f"رویکرد کسب‌وکار «برتری عملیاتی» شد."))
