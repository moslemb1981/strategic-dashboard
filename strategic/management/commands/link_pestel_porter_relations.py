# -*- coding: utf-8 -*-
"""
این دستور فقط ارتباط‌هایی رو ثبت می‌کنه که از نظر محتوایی کاملاً روشن و بدون ابهامه —
نه هر ۱۹۰ ذینفع/۱۱۱ الزام رو به‌زور به یه عامل وصل می‌کنه. تطبیق‌ها بر اساس تطبیق متنی
(نه شماره‌ی ردیف که ممکنه بین سیستم‌ها فرق کنه) انجام می‌شه، پس اگه یه ردیف با متن دقیق پیدا
نشه، فقط رد می‌شه و توی گزارش نهایی اعلام می‌شه، بدون خطا.
"""
from django.core.management.base import BaseCommand
from strategic.models import LegalRequirement, PestelFactor, PorterForce, Stakeholder


def _norm(s):
    return (s or "").replace("\u200c", "").replace(" ", "").strip()


class Command(BaseCommand):
    help = "ارتباط‌های منطقی و مطمئن بین PESTEL/Porter و ذینفعان/الزامات قانونی را ثبت می‌کند (فقط موارد بدون ابهام)."

    def handle(self, *args, **options):
        pestel_by_text = {_norm(f.text): f for f in PestelFactor.objects.all()}
        porter_by_text = {_norm(f.text): f for f in PorterForce.objects.all()}
        legal_by_title = {}
        for lr in LegalRequirement.objects.all():
            legal_by_title.setdefault(_norm(lr.title), []).append(lr)
        stake_by_name = {}
        for s in Stakeholder.objects.all():
            stake_by_name.setdefault(_norm(s.name), []).append(s)

        report = {"legal_pestel": 0, "stake_porter": 0, "stake_pestel": 0, "not_found": []}

        # ---------------- ۱) الزامات قانونی → PESTEL (تک‌انتخابی، ثبت روی خود الزام) ----------------
        # فقط الزاماتی که موضوعشون دقیقاً با یکی از عوامل PESTEL یکی است.
        LEGAL_TO_PESTEL = [
            # (بخشی از عنوان الزام که در آن جست‌وجو می‌شود، متن دقیق عامل PESTEL مقصد)
            ("ISO9001", "استانداردهای مدیریتی شامل 9000،10002،10004،10015،14001"),
            ("ISO10002", "استانداردهای مدیریتی شامل 9000،10002،10004،10015،14001"),
            ("ISO10004", "استانداردهای مدیریتی شامل 9000،10002،10004،10015،14001"),
            ("ISO10015", "استانداردهای مدیریتی شامل 9000،10002،10004،10015،14001"),
            ("ISO14001", "استانداردهای مدیریتی شامل 9000،10002،10004،10015،14001"),
            ("بخشنامه ها، آئین نامه ها و ابلاغیه های سایپا", "قوانین، استانداردها و تنظیم گری"),
            ("قانون حمایت از مصرف کنندگان", "قوانین، استانداردها و تنظیم گری"),
            ("دستوالعمل اجرایی آئین نامه قانون حمایت از حقوق مصرف کنندگان", "قوانین، استانداردها و تنظیم گری"),
            ("رعايت قانون حمايت از حقوق مصرف", "قوانین، استانداردها و تنظیم گری"),
            ("رعایت حقوق مشتری در عرضه", "قوانین، استانداردها و تنظیم گری"),
            ("تغییر سیستم هماهنگ شده", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("مقررات صادرات و واردات", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("مقررات واردات و صادرات", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("الزامات بین المللی اعتبار اسنادی", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("اینکو ترمز", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("حمل و ترافیک دریایی", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("پحمل و ترافیک دریایی", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("بیمه های حمل و نقل کالا", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("بیه های حمل و نقل دریایی", "ارتباطات بین‌المللی (تحریم، جنگ، ارتباطات منطقه ای)"),
            ("رعايت مقررات مالیاتی در تسويه حساب", "قوانین جدید مربوط به سامانه مودیان مالیاتی"),
            ("رعایت الزامات زیست‌محیطی در بسته‌بندی", "مدیریت پسماند و بازیافت"),
            ("استاندارد 85 گانه قطعات خودرویی", "استاندارد 122 گانه خودرو"),
            ("الزامات سازمان بازرسي کیفیت (ISQI)", "تشدید نظارت بر استانداردهای مدیریت کیفیت قطعات و خدمات(ISQI )"),
            ("قانون تامین اجتماعی", "مقررات مربوط به ایمنی و بهداشت کار/ بیمه"),
            ("فصل چهارم قانون کار", "مقررات مربوط به ایمنی و بهداشت کار/ بیمه"),
        ]
        # همه‌ی الزامات معاونت منابع انسانی که موضوعشون آیین‌نامه‌های ایمنی/بهداشت/حفاظت کار است
        HSE_KEYWORDS = ["آئین نامه ایمنی", "آئین نامه حفاظت", "ائین نامه ایمنی", "آئین نامه حفاظتی",
                        "آئین نامه علائم ایمنی", "آئین نامه وسایل حفاظت", "آئین نامه پیشگیری و مبارزه با آتش",
                        "آئین نامه کمیته حفاظت", "دستورالعمل های بهداشت حرفه ای", "ابلاغیه مراکز بهداشت",
                        "دفترچه حدود مجازر تماس شغلی", "مبحث 12"]

        for lr in LegalRequirement.objects.all():
            target_text = None
            for keyword, pestel_text in LEGAL_TO_PESTEL:
                if _norm(keyword) in _norm(lr.title):
                    target_text = pestel_text
                    break
            if not target_text and any(_norm(k) in _norm(lr.title) for k in HSE_KEYWORDS):
                target_text = "مقررات مربوط به ایمنی و بهداشت کار/ بیمه"
            if target_text:
                pf = pestel_by_text.get(_norm(target_text))
                if pf and lr.related_pestel_id != pf.pk:
                    lr.related_pestel = pf
                    lr.save(update_fields=["related_pestel"])
                    report["legal_pestel"] += 1
                elif not pf:
                    report["not_found"].append(f"PESTEL not found for legal->pestel rule: {target_text}")

        # ---------------- ۲) ذینفعان → Porter (چندانتخابی، ثبت روی خود ذینفع) ----------------
        STAKE_TO_PORTER = [
            # (بخشی از نام ذینفع، لیست متن دقیق عامل/عوامل Porter مقصد)
            ("تامین کنندگان قطعه آپشن", ["نقش تأمین‌کنندگان", "پایبندی به تعهدات مالی (نظم پرداختی)"]),
            ("تامین کنندگان قطعات", ["نقش تأمین‌کنندگان", "پایبندی به تعهدات مالی (نظم پرداختی)"]),
            ("تامین کنندگان", ["نقش تأمین‌کنندگان", "پایبندی به تعهدات مالی (نظم پرداختی)"]),
            ("پیمانکاران نصب آپشن", ["نقش تأمین‌کنندگان"]),
            ("پیمانکار جمع آوری داغی", ["نقش تأمین‌کنندگان"]),
            ("پیمانکار نگهداری و تعمیرات تجهیزات", ["نقش تأمین‌کنندگان"]),
            ("شبکه نمایندگیها", ["عدم تطابق اعتبار عوامل فروش قطعه شبکه با بدهی (موضوع اجرایی درون سازمانی)"]),
            ("شبکه نمایندگیها/ تعمیرگاه مرکزی", ["عدم تطابق اعتبار عوامل فروش قطعه شبکه با بدهی (موضوع اجرایی درون سازمانی)"]),
            ("نمایندگان مجاز شبکه", ["عدم تطابق اعتبار عوامل فروش قطعه شبکه با بدهی (موضوع اجرایی درون سازمانی)"]),
            ("شبکه فروش قطعات", ["عدم تطابق اعتبار عوامل فروش قطعه شبکه با بدهی (موضوع اجرایی درون سازمانی)"]),
            ("مشتریان", ["افزایش تمایل مشتریان به تحویل سریع قطعات",
                         "کاهش خریداران بدلیل نبود تضمین گارانتی قطعات تجاری"]),
        ]
        for name_key, porter_texts in STAKE_TO_PORTER:
            candidates = stake_by_name.get(_norm(name_key), [])
            targets = [porter_by_text.get(_norm(t)) for t in porter_texts]
            targets = [t for t in targets if t]
            if not targets:
                report["not_found"].append(f"Porter not found for stakeholder rule: {name_key}")
                continue
            for s in candidates:
                for t in targets:
                    if not s.related_porters.filter(pk=t.pk).exists():
                        s.related_porters.add(t)
                        report["stake_porter"] += 1

        # ---------------- ۳) PESTEL → ذینفعان (چندانتخابی، ثبت روی خود عامل PESTEL) ----------------
        STAKE_TO_PESTEL = [
            ("سازمان های نظارتی و ممیزی", "قوانین، استانداردها و تنظیم گری"),
            ("سازمان حسابرسی", "قوانین، استانداردها و تنظیم گری"),
            ("سازمان های بالا دستی", "قوانین، استانداردها و تنظیم گری"),
        ]
        for name_key, pestel_text in STAKE_TO_PESTEL:
            candidates = stake_by_name.get(_norm(name_key), [])
            pf = pestel_by_text.get(_norm(pestel_text))
            if not pf:
                report["not_found"].append(f"PESTEL not found for stakeholder->pestel rule: {pestel_text}")
                continue
            for s in candidates:
                if not pf.related_stakeholders.filter(pk=s.pk).exists():
                    pf.related_stakeholders.add(s)
                    report["stake_pestel"] += 1

        self.stdout.write(self.style.SUCCESS(
            f"ثبت شد: {report['legal_pestel']} ارتباط الزام‌قانونی←PESTEL، "
            f"{report['stake_porter']} ارتباط ذینفع←Porter، "
            f"{report['stake_pestel']} ارتباط PESTEL←ذینفع."
        ))
        if report["not_found"]:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده (رد شدند، بدون خطا):"))
            for msg in report["not_found"]:
                self.stdout.write("  - " + msg)
