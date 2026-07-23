# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from strategic.models import PorterForce

DATA = {
    "rivalry": {
        "level": "high",
        "reasons": [
            "رقابت شدید با بازار قطعات متفرقه، چینی ارزان‌قیمت و تأمین‌کنندگان غیررسمی.",
            "تعداد زیاد تعمیرگاه‌های آزاد با قیمت کمتر و سرعت بیشتر.",
            "فشار مستمر مشتری برای «قیمت کمتر و تحویل سریع‌تر».",
        ],
        "conclusion": "تهدید جدی برای فروش قطعات برند یک و کاهش سهم بازار اصلی.",
    },
    "buyer_power": {
        "level": "very_high",
        "reasons": [
            "کاهش قدرت خرید → حساسیت شدید به قیمت.",
            "وجود جایگزین‌های ارزان.",
            "ابزارهای شبکه اجتماعی برای مقایسه قیمت و شکایت.",
        ],
        "conclusion": "سایپا یدک مجبور به رقابت قیمتی و افزایش کیفیت پاسخگویی است.",
    },
    "supplier_power": {
        "level": "high",
        "reasons": [
            "بخش قابل توجهی از MRP خارجی با تأخیر و عملکرد پایین (۲۰–۳۰٪).",
            "قطعات انحصاری برخی خودروها از خارج تأمین می‌شود.",
            "مشکلات نقدینگی سایپا یدک → کاهش توان پرداخت نقدی و کاهش جذابیت برای تأمین‌کنندگان.",
        ],
        "conclusion": "ریسک کمبود قطعه و افزایش قیمت تمام‌شده.",
    },
    "new_entrants": {
        "level": "medium",
        "reasons": [
            "ورود برندهای چینی جدید که شبکه قطعات مستقل دارند.",
            "پلتفرم‌های دیجیتال فروش قطعه و مارکت‌پلیس‌ها.",
        ],
        "conclusion": "تهدیدی برای سهم بازار سنتی سایپا یدک.",
    },
    "substitutes": {
        "level": "very_high",
        "reasons": [
            "قطعات غیراوریجینال با قیمت‌های بسیار پایین‌تر.",
            "استفاده مجدد از قطعات استوک و بازسازی‌شده.",
            "تعمیر به‌جای تعویض به دلیل گرانی قطعات.",
        ],
        "conclusion": "افت فروش برند یک و کاهش سود.",
    },
}


class Command(BaseCommand):
    help = "تحلیل واقعی پنج نیروی پورتر سایپا یدک را ثبت/به‌روزرسانی می‌کند."

    def handle(self, *args, **options):
        for force, d in DATA.items():
            PorterForce.objects.update_or_create(
                force=force,
                defaults={
                    "level": d["level"],
                    "reasons": "\n".join(d["reasons"]),
                    "conclusion": d["conclusion"],
                },
            )
        self.stdout.write(self.style.SUCCESS("هر ۵ نیروی پورتر با داده‌ی واقعی ثبت/به‌روزرسانی شد."))
