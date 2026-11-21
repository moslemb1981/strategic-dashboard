from django.core.management.base import BaseCommand
from strategic.models import Competitor

COMPETITORS = [
    # name, market_share, strengths, weaknesses, recent_move, order
    ("تولیدکنندگان داخلی OEM", 38,
     "شبکه توزیع گسترده\nهزینه تولید پایین‌تر", "تنوع محدود قطعات",
     "افزایش ظرفیت تولید در فصل اخیر", 1),
    ("واردکنندگان رسمی", 27,
     "کیفیت و برند شناخته‌شده", "حساس به نوسان ارز\nزمان تحویل طولانی‌تر",
     "کاهش سفارش به دلیل تعرفه جدید", 2),
    ("بازار غیررسمی/تقلبی", 20,
     "قیمت بسیار پایین", "کیفیت و ضمانت نامطمئن",
     "ریسک برای اعتبار برند در بازار", 3),
    ("سایر تولیدکنندگان داخلی", 15,
     "انعطاف در سفارش‌های کوچک", "ظرفیت تولید محدود",
     "بدون تغییر محسوس در سه‌ماهه اخیر", 4),
]


class Command(BaseCommand):
    help = "چهار بازیگر نمونه بازار قطعات یدکی را به‌عنوان الگو ثبت می‌کند (اجرای دوباره، تکراری نمی‌سازد)."

    def handle(self, *args, **options):
        created = 0
        for name, share, strengths, weaknesses, move, order in COMPETITORS:
            obj, was_created = Competitor.objects.get_or_create(
                name=name,
                defaults=dict(market_share=share, strengths=strengths, weaknesses=weaknesses,
                              recent_move=move, order=order),
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"{created} بازیگر جدید ثبت شد (از ۴ مورد نمونه)."))
