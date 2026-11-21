from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("strategic", "0113_scorecard_signatures")]
    operations = [
        migrations.CreateModel(
            name="ScorecardSnapshot",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("owner_key", models.CharField(db_index=True, max_length=20, verbose_name="کلید واحد")),
                ("year", models.PositiveSmallIntegerField(verbose_name="سال")),
                ("month", models.PositiveSmallIntegerField(verbose_name="ماه")),
                ("data", models.TextField(verbose_name="داده‌ی کارنامه (JSON)")),
                ("finalized_at", models.DateTimeField(auto_now_add=True, verbose_name="زمان نهایی‌سازی")),
                ("finalized_by", models.CharField(blank=True, max_length=150, verbose_name="نهایی‌کننده")),
            ],
            options={
                "verbose_name": "نسخه نهایی کارنامه",
                "verbose_name_plural": "نسخه‌های نهایی کارنامه",
                "unique_together": {("owner_key", "year", "month")},
            },
        ),
    ]
