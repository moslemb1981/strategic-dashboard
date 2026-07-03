from django.core.management.base import BaseCommand
from strategic.models import Risk

RISKS = [
    # title, owner, likelihood(1-4), impact(1-4), mitigation
    ("افزایش شدید نرخ ارز", "مدیریت مالی", 4, 4,
     "پوشش ارزی بخشی از قراردادها و بازنگری فصلی قیمت‌گذاری"),
    ("وقفه در زنجیره تأمین منطقه‌ای", "واحد توسعه", 2, 4,
     "تنوع‌بخشی به تأمین‌کنندگان و ذخیره احتیاطی راهبردی"),
    ("گسترش بازار غیررسمی و قطعات تقلبی", "هوش رقابتی", 3, 3,
     "کمپین آگاهی‌بخشی برند و همکاری با نهادهای نظارتی"),
    ("کاهش کیفیت قطعات وارداتی", "کنترل کیفیت", 2, 3,
     "ممیزی دوره‌ای تأمین‌کنندگان و آزمون نمونه ورودی"),
    ("تغییر مقررات واردات قطعات", "امور حقوقی", 3, 2,
     "پایش مستمر تغییرات قانونی و سناریوسازی پیشینی"),
    ("کمبود نیروی متخصص تحلیل داده", "منابع انسانی", 2, 2,
     "برنامه آموزش داخلی و جذب هدفمند نیروی متخصص"),
]


class Command(BaseCommand):
    help = "شش ریسک نمونه نزدیک به عملکرد یک شرکت قطعات یدکی را به‌عنوان الگو ثبت می‌کند (اجرای دوباره، تکراری نمی‌سازد)."

    def handle(self, *args, **options):
        created = 0
        for title, owner, likelihood, impact, mitigation in RISKS:
            obj, was_created = Risk.objects.get_or_create(
                title=title,
                defaults=dict(owner=owner, likelihood=likelihood, impact=impact, mitigation=mitigation),
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"{created} ریسک جدید ثبت شد (از ۶ مورد نمونه). موارد از قبل موجود دست‌نخورده ماندند."
        ))
