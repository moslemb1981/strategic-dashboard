# -*- coding: utf-8 -*-
"""پاک‌سازی امن پروژه‌های تکراری — طبق باگ کشف‌شده در ورودی اکسل (که تشخیص
پروژه‌ی موجود رو بر پایه‌ی «عنوان+کسب‌وکار» انجام می‌داد، نه کد؛ برای همین وقتی
کسب‌وکار عوض شد، به‌جای به‌روزرسانی، رکورد تازه ساخته شد).

روش کار: برای هر گروه‌عنوان تکراری، رکورد با کمترین شناسه (pk) — که معمولاً
همون رکورد قدیمی و پر از ارتباطات تاریخیه — به‌عنوان «بازمانده» انتخاب می‌شه.
قبل از حذف بقیه‌ی نسخه‌ها، هر ارتباطی (هدف/شاخص کلان/شاخص عملیاتی/TOWS/ریسک/
ذینفع) که روی نسخه‌های دیگه بود، به بازمانده منتقل می‌شه — تا هیچ داده‌ای گم
نشه، از جمله همون ۸ ارتباط TOWS که اشتباهاً روی نسخه‌ی خالی نشسته بودن."""
from django.core.management.base import BaseCommand
from django.db.models import Count
from strategic.models import Initiative, Stakeholder


class Command(BaseCommand):
    help = "پروژه‌های تکراری (ناشی از باگ ورودی اکسل) را با ادغام کامل ارتباطات، پاک‌سازی می‌کند."

    def handle(self, *args, **options):
        dup_titles = (
            Initiative.objects.values("title")
            .annotate(cnt=Count("id"))
            .filter(cnt__gt=1)
        )
        total_groups = 0
        total_deleted = 0
        total_merged_links = 0

        for row in dup_titles:
            title = row["title"]
            records = list(Initiative.objects.filter(title=title).order_by("pk"))
            survivor = records[0]
            duplicates = records[1:]
            total_groups += 1

            for dup in duplicates:
                # ادغام M2M های خودِ Initiative
                for field in ["objectives", "source_kpi", "source_operational_kpi", "source_tows", "source_risk"]:
                    dup_related = getattr(dup, field).all()
                    if dup_related.exists():
                        getattr(survivor, field).add(*dup_related)
                        total_merged_links += dup_related.count()

                # ادغام ارتباط معکوس از ذینفعان (Stakeholder.related_initiatives)
                stakeholders_linked = Stakeholder.objects.filter(related_initiatives=dup)
                for sh in stakeholders_linked:
                    sh.related_initiatives.add(survivor)
                    sh.related_initiatives.remove(dup)
                    total_merged_links += 1

                # اگه بازمانده فیلد مهمی خالی داشت ولی نسخه‌ی تکراری پر بود، منتقل کن
                for f in ["code", "owner", "division", "work_group", "business_unit_id",
                          "start_date", "end_date"]:
                    if not getattr(survivor, f) and getattr(dup, f):
                        setattr(survivor, f, getattr(dup, f))

                dup.delete()
                total_deleted += 1

            survivor.save()

        self.stdout.write(self.style.SUCCESS(
            f"پاک‌سازی انجام شد: {total_groups} گروه تکراری، {total_deleted} رکورد حذف شد، "
            f"{total_merged_links} ارتباط منتقل شد."
        ))
        remaining = Initiative.objects.count()
        self.stdout.write(f"تعداد پروژه‌ی باقی‌مانده: {remaining}")
