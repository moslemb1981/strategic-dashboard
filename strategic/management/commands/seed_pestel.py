from django.core.management.base import BaseCommand
from strategic.models import PestelFactor

FACTORS = [
    # category, text, order
    ("political", "تغییرات سیاست‌های تجاری و تعرفه‌ای", 1),
    ("political", "تحریم‌ها و محدودیت‌های واردات قطعات", 2),
    ("economic", "نوسان نرخ ارز و تورم مواد اولیه", 1),
    ("economic", "کاهش قدرت خرید مصرف‌کننده نهایی", 2),
    ("social", "افزایش سن ناوگان خودرویی کشور", 1),
    ("social", "تغییر ترجیح مشتریان به قطعات باکیفیت", 2),
    ("technological", "رشد خودروهای متصل و هوشمند", 1),
    ("technological", "دیجیتالی‌شدن زنجیره تأمین و انبارداری", 2),
    ("environmental", "الزامات کاهش آلایندگی خودرو", 1),
    ("environmental", "فشار قانونی برای بازیافت قطعات فرسوده", 2),
    ("legal", "استانداردهای اجباری کیفیت قطعات", 1),
    ("legal", "مقررات ضمانت و خدمات پس از فروش", 2),
]


class Command(BaseCommand):
    help = "دوازده عامل نمونه PESTEL را به‌عنوان الگو ثبت می‌کند (اجرای دوباره، تکراری نمی‌سازد)."

    def handle(self, *args, **options):
        created = 0
        for category, text, order in FACTORS:
            obj, was_created = PestelFactor.objects.get_or_create(
                category=category, text=text, defaults=dict(order=order),
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} عامل جدید ثبت شد (از ۱۲ مورد نمونه)."))
