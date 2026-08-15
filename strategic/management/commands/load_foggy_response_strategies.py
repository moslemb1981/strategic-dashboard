# -*- coding: utf-8 -*-
"""بارگذاری راهبردهای تقویت و بهبود عملکرد تاب‌آوری سازمانی برای سناریوی «هوای مه‌آلود»."""
from django.core.management.base import BaseCommand
from strategic.models import Scenario, ScenarioResponseStrategy

STRATEGIES = [
    ("افزایش درآمد", ""),
    ("کاهش مصرف انرژی", "ISO 50001 — سیستم مدیریت انرژی"),
    ("کاهش هزینه‌های غیر ضروری", "ISO 9001 — مدیریت کیفیت"),
    ("افزایش تاب‌آوری در شرایط بحران", "ISO 22301 — مدیریت تداوم کسب‌وکار"),
    ("اقدامات ابتکاری و خلاقانه در بهره‌برداری از فرصت‌های محیطی", "ISO 14001 — مدیریت محیط زیست"),
    ("چابک‌سازی و بهره‌ورسازی سیستم‌ها و فرآیندها", ""),
    ("مدیریت بهینه‌تر نقدینگی", ""),
    ("افزایش دسترسی به قطعات و خدمات در دوره گارانتی", ""),
    ("قیمت‌گذاری هدفمند و هوشمند قطعات", ""),
    ("توزیع مستقیم و هوشمند قطعات در سطح شبکه", ""),
    ("تأمین منابع مالی", ""),
    ("افزایش رضایت مشتریان", "ISO 10002 و ISO 10004 — رضایت و رسیدگی به شکایات مشتریان"),
    ("افزایش تعلق خاطر و شور و نشاط کارکنان", ""),
    ("رعایت استانداردهای مدیریتی", "ISO 9001، 10002، 10004، 10015، 14001"),
]


class Command(BaseCommand):
    help = "راهبردهای پاسخ به سناریوی هوای مه‌آلود را بارگذاری می‌کند."

    def handle(self, *args, **options):
        scenario, _ = Scenario.objects.get_or_create(quadrant="foggy")
        scenario.response_strategies.all().delete()
        objs = [
            ScenarioResponseStrategy(scenario=scenario, text=text, related_standard=std, order=i)
            for i, (text, std) in enumerate(STRATEGIES, start=1)
        ]
        ScenarioResponseStrategy.objects.bulk_create(objs)
        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {len(objs)} راهبرد برای سناریوی «هوای مه‌آلود»."))
