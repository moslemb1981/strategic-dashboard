from django.core.management.base import BaseCommand
from strategic.models import StrategicObjective

OBJECTIVES = [
    # code, perspective, theme, title, kpi, status, order
    ("F1", "financial", "operational", "کاهش هزینه‌های عملیاتی زنجیره تأمین", "کاهش ۸٪ هزینه سرانه توزیع", "on", 1),
    ("F2", "financial", "growth", "افزایش سودآوری خالص و رشد فروش آفترمارکت", "رشد ۱۲٪ حاشیه سود ناخالص", "on", 2),
    ("F3", "financial", "digital", "بهبود بازده سرمایه‌گذاری فناوری", "ROI پروژه‌های دیجیتال ≥ ۲۰٪", "watch", 3),

    ("C1", "customer", "operational", "کاهش زمان تحویل سفارش به نمایندگی‌ها", "OTIF ≥ ۹۵٪", "on", 1),
    ("C2", "customer", "growth", "افزایش رضایت و وفاداری نمایندگی‌ها", "شاخص NPS نمایندگان ≥ ۷۰", "watch", 2),
    ("C3", "customer", "digital", "بهبود تجربه سفارش‌گذاری آنلاین مشتریان", "نرخ تکمیل سفارش آنلاین ≥ ۸۰٪", "risk", 3),

    ("P1", "process", "operational", "استانداردسازی کنترل کیفیت قطعات", "نرخ مرجوعی زیر ۱٪", "on", 1),
    ("P2", "process", "growth", "بهبود برنامه‌ریزی تولید و توزیع منطقه‌ای", "دقت پیش‌بینی تقاضا ≥ ۹۰٪", "on", 2),
    ("P3", "process", "digital", "دیجیتالی‌سازی فرآیند انبارداری و موجودی", "پوشش سیستمی انبارها ≥ ۷۵٪", "watch", 3),

    ("L1", "learning", "operational", "آموزش تخصصی فرآیندهای ناب (لین)", "۸۰٪ کارکنان کلیدی دوره‌دیده", "on", 1),
    ("L2", "learning", "growth", "جذب و توسعه نیروی متخصص فروش و بازاریابی", "تکمیل ۹۰٪ ظرفیت تیم فروش", "watch", 2),
    ("L3", "learning", "digital", "توسعه مهارت‌های تحلیل داده و ابزارهای دیجیتال", "۵۰٪ کارکنان اداره دوره‌دیده", "risk", 3),
]


class Command(BaseCommand):
    help = "دوازده هدف نمونه‌ی نقشه استراتژیک را به‌عنوان الگو در دیتابیس ثبت می‌کند (اجرای دوباره، تکراری نمی‌سازد)."

    def handle(self, *args, **options):
        created = 0
        for code, perspective, theme, title, kpi, status, order in OBJECTIVES:
            obj, was_created = StrategicObjective.objects.get_or_create(
                code=code,
                defaults=dict(
                    perspective=perspective, theme=theme, title=title,
                    kpi=kpi, status=status, order=order,
                ),
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"{created} هدف جدید ثبت شد (از ۱۲ مورد نمونه). موارد از قبل موجود دست‌نخورده ماندند."
        ))
