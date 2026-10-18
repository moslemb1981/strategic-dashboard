from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0106_sectionvisibility"),
    ]

    operations = [
        migrations.AddField(
            model_name="functionalstrategy",
            name="linked_operational_kpis",
            field=models.ManyToManyField(
                blank=True, related_name="functional_strategies",
                to="strategic.operationalkpi", verbose_name="شاخص‌های عملیاتی مرتبط",
            ),
        ),
    ]
