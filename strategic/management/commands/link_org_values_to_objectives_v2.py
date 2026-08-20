# -*- coding: utf-8 -*-
"""بازسازی کامل اتصال ۸ ارزش سازمانی به اهداف استراتژیک — نسخه‌ی دقیق‌شده،
جایگزین نسخه‌ی اولیه‌ی بند ۱۸۹ که خیلی محدود بود (مثلاً «نوآوری بازار محور»
فقط ۲ هدف داشت، درحالی‌که ۲۱ هدف با محور «نوآوری» در کل ۵ کسب‌وکار وجود داره).

روش کار:
۱) برای ۵ ارزشی که دقیقاً معادل یکی از محورهای نقشه‌ی استراتژیک هستن، تمام
   اهداف اون محور را در هر ۵ کسب‌وکار (هرجا محور وجود داشته باشه) وصل می‌کنیم —
   پوشش کامل، نه چندتا نمونه‌ی دستی.
۲) برای ۳ ارزشی که معادل مستقیم محوری ندارن (رقابت سالم، شفافیت و اعتمادآفرینی،
   اطلاع‌رسانی جامع به ذی‌نفعان)، همون تطبیق محتوایی دقیق قبلی (بند ۱۸۹) حفظ
   می‌شه — چون این‌ها موضوعاتی هستن که یه محور اختصاصی توی نقشه‌ی استراتژیک
   ندارن، پس تطبیق محتوایی هنوز بهترین روشه."""
from django.core.management.base import BaseCommand
from strategic.models import OrgValue, StrategicObjective


# ارزش‌هایی که دقیقاً معادل یه محور مشخص‌اند — همه‌ی اهداف اون محور (در هر
# کسب‌وکاری که وجود داشته باشه) وصل می‌شن
VALUE_TO_THEMES = {
    "کرامت انسانی ناظر بر حقوق ذی‌نفعان": ["مسئولیت‌های قانونی و اجتماعی"],
    "توان‌افزایی و توسعه قابلیت‌های کارکنان": ["سرمایه انسانی"],
    "نوآوری بازار محور": ["نوآوری"],
    "وحدت و کارتیمی": ["سرمایه سازمانی"],
    "مشتری‌مداری": ["مدیریت مشتری", "مشتری نهایی", "مدیریت روابط با مشتریان"],
}

# ارزش‌هایی که معادل محور مستقیم ندارن — تطبیق محتوایی دستی (از بند ۱۸۹، هنوز معتبر)
VALUE_TO_OBJECTIVE_PKS = {
    "رقابت سالم": [8, 102],
    "شفافیت و اعتمادآفرینی": [96, 82],
    "اطلاع‌رسانی جامع به ذی‌نفعان": [130, 163],
}


class Command(BaseCommand):
    help = "اتصال ۸ ارزش سازمانی به اهداف استراتژیک را به‌صورت کامل (بر پایه‌ی محور) بازسازی می‌کند."

    def handle(self, *args, **options):
        total = 0
        not_found = []

        for value_text, theme_names in VALUE_TO_THEMES.items():
            try:
                value = OrgValue.objects.get(text=value_text)
            except OrgValue.DoesNotExist:
                not_found.append(f"ارزش «{value_text}» یافت نشد")
                continue
            objs = StrategicObjective.objects.filter(theme__name__in=theme_names)
            value.related_objectives.set(objs)
            total += objs.count()
            self.stdout.write(f"  {value_text}: {objs.count()} هدف (بر پایه‌ی محور {theme_names})")

        for value_text, obj_pks in VALUE_TO_OBJECTIVE_PKS.items():
            try:
                value = OrgValue.objects.get(text=value_text)
            except OrgValue.DoesNotExist:
                not_found.append(f"ارزش «{value_text}» یافت نشد")
                continue
            objs = StrategicObjective.objects.filter(pk__in=obj_pks)
            value.related_objectives.set(objs)
            total += objs.count()
            self.stdout.write(f"  {value_text}: {objs.count()} هدف (تطبیق محتوایی دستی)")

        self.stdout.write(self.style.SUCCESS(f"\nجمع کل: {total} ارتباط ارزش-هدف ثبت شد."))
        if not_found:
            self.stdout.write(self.style.WARNING("موارد یافت‌نشده:"))
            for msg in not_found:
                self.stdout.write("  - " + msg)
