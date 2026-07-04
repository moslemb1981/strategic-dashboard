from django.core.management.base import BaseCommand
from strategic.models import BusinessUnit, StrategicObjective, SWOTItem, TOWSStrategy

BUSINESS_UNITS = [
    ("کسب و کار بسته خدمت", "intimacy", 1),
    ("کسب و کار گارانتی خودرو", "excellence", 2),
    ("کسب و کار بازرگانی قطعات", "exclusive", 3),
    ("کسب و کار آپشن", "exclusive", 4),
    ("کسب و کار خدمات تعمیراتی", "intimacy", 5),
]

# اگه دستور نسخه‌ی قبلی (با اسم‌های اشتباه) قبلاً اجرا شده باشه، این‌ها رو
# به اسم درست تغییر نام می‌دیم به‌جای اینکه رکورد تکراری بسازیم.
RENAME_FROM_OLD = {
    "کسب‌وکار بسته خدمت": "کسب و کار بسته خدمت",
    "کسب‌وکار کارگزاری خودرو": "کسب و کار گارانتی خودرو",
    "کسب‌وکار بازرگانی قطعات یدکی": "کسب و کار بازرگانی قطعات",
    "کسب‌وکار آپشن": "کسب و کار آپشن",
    "کسب‌وکار خدمات تعمیراتی": "کسب و کار خدمات تعمیراتی",
}


class Command(BaseCommand):
    help = (
        "پنج کسب‌وکار واقعی سایپا یدک را می‌سازد (یا اسم نسخه‌ی قبلی را اصلاح می‌کند) و داده‌های "
        "فعلی نقشه استراتژیک/SWOT را به کسب‌وکار «بازرگانی قطعات» متصل می‌کند. اجرای دوباره امن است."
    )

    def handle(self, *args, **options):
        renamed = 0
        for old_name, new_name in RENAME_FROM_OLD.items():
            updated = BusinessUnit.objects.filter(name=old_name).update(name=new_name)
            renamed += updated

        created = 0
        units = {}
        for name, archetype, order in BUSINESS_UNITS:
            bu, was_created = BusinessUnit.objects.get_or_create(
                name=name, defaults={"archetype": archetype, "order": order},
            )
            if not was_created:
                BusinessUnit.objects.filter(pk=bu.pk).update(archetype=archetype, order=order)
            units[name] = bu
            if was_created:
                created += 1

        parts_bu = units["کسب و کار بازرگانی قطعات"]

        obj_updated = StrategicObjective.objects.filter(business_unit__isnull=True).update(business_unit=parts_bu)
        swot_updated = SWOTItem.objects.filter(business_unit__isnull=True).update(business_unit=parts_bu)
        tows_updated = TOWSStrategy.objects.filter(business_unit__isnull=True).update(business_unit=parts_bu)

        self.stdout.write(self.style.SUCCESS(
            f"{renamed} کسب‌وکار قدیمی به اسم درست تغییر یافت. {created} کسب‌وکار جدید ساخته شد (از ۵ مورد).\n"
            f"داده‌های بدون کسب‌وکار به «بازرگانی قطعات» وصل شدند: "
            f"{obj_updated} هدف استراتژیک، {swot_updated} مورد SWOT، {tows_updated} راهبرد TOWS."
        ))
