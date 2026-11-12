import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0110_kpi_analysis_report"),
    ]

    operations = [
        migrations.CreateModel(
            name="BusinessCanvasItem",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("block", models.CharField(choices=[("partners", "شرکای کلیدی"), ("activities", "فعالیت‌های کلیدی"), ("resources", "منابع کلیدی"), ("value", "پیشنهاد ارزش"), ("relations", "ارتباط با مشتری"), ("channels", "کانال‌ها"), ("segments", "بخش‌های مشتریان"), ("costs", "ساختار هزینه"), ("revenue", "جریان‌های درآمدی")], max_length=12, verbose_name="بلوک")),
                ("text", models.CharField(max_length=300, verbose_name="متن")),
                ("note", models.TextField(blank=True, default="", verbose_name="توضیح / منبع")),
                ("status", models.CharField(choices=[("approved", "تأیید شده"), ("draft", "پیش‌نویس (نیازمند تأیید)")], default="approved", max_length=10, verbose_name="وضعیت")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب")),
                ("created_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("business_unit", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="canvas_items", to="strategic.businessunit", verbose_name="کسب‌وکار")),
            ],
            options={
                "verbose_name": "مورد بوم کسب‌وکار",
                "verbose_name_plural": "موارد بوم کسب‌وکار",
                "ordering": ["business_unit", "block", "order", "id"],
            },
        ),
    ]
