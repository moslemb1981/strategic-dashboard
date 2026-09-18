# -*- coding: utf-8 -*-
"""افزودن وزن به شاخص‌های هر کارت هدف استراتژیک — قدم ۱ از ۳.
این قدم فقط دو جدول جدید (وزن شاخص کلان / وزن شاخص عملیاتی برای هر کارت) می‌سازد.
هیچ داده‌ای هنوز جابه‌جا یا حذف نمی‌شود."""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategic', '0093_operationalkpi_is_confidential'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectiveKPIWeight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveIntegerField(default=100, verbose_name='وزن شاخص در این کارت (۱ تا ۱۰۰)')),
                ('kpi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strategic.companykpi')),
                ('objective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strategic.strategicobjective')),
            ],
            options={
                'verbose_name': 'وزن شاخص کلان در کارت هدف',
                'verbose_name_plural': 'وزن شاخص‌های کلان در کارت‌های هدف',
                'unique_together': {('objective', 'kpi')},
            },
        ),
        migrations.CreateModel(
            name='ObjectiveOperationalKPIWeight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.PositiveIntegerField(default=100, verbose_name='وزن شاخص در این کارت (۱ تا ۱۰۰)')),
                ('kpi', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strategic.operationalkpi')),
                ('objective', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='strategic.strategicobjective')),
            ],
            options={
                'verbose_name': 'وزن شاخص عملیاتی در کارت هدف',
                'verbose_name_plural': 'وزن شاخص‌های عملیاتی در کارت‌های هدف',
                'unique_together': {('objective', 'kpi')},
            },
        ),
    ]
