# -*- coding: utf-8 -*-
"""افزودن وزن به شاخص‌های هر کارت هدف استراتژیک — قدم ۳ از ۳ (نهایی).
حالا که داده‌ها با وزن ۱۰۰ در جدول‌های جدید کپی شدند (قدم ۲)، فیلدهای چندارتباطی
قدیمی linked_kpis / linked_operational_kpis (که به جدول واسط خودکار جنگو وصل بودند)
برداشته می‌شوند و همان دو فیلد، این‌بار با اتصال به جدول‌های وزن‌دار جدید، دوباره
اضافه می‌شوند. چون جدول‌های جدید از قبل ساخته و پر شده‌اند، هیچ داده‌ای از دست
نمی‌رود — فقط جنگو دیگر از جدول واسط خودکار قدیمی (که خالی از این پس می‌ماند)
استفاده نمی‌کند."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategic', '0095_objective_kpi_weight_data'),
    ]

    operations = [
        migrations.RemoveField(model_name='strategicobjective', name='linked_kpis'),
        migrations.RemoveField(model_name='strategicobjective', name='linked_operational_kpis'),
        migrations.AddField(
            model_name='strategicobjective',
            name='linked_kpis',
            field=models.ManyToManyField(blank=True, related_name='strategic_objectives', through='strategic.ObjectiveKPIWeight', to='strategic.companykpi', verbose_name='شاخص‌های استراتژیک مرتبط'),
        ),
        migrations.AddField(
            model_name='strategicobjective',
            name='linked_operational_kpis',
            field=models.ManyToManyField(blank=True, related_name='strategic_objectives', through='strategic.ObjectiveOperationalKPIWeight', to='strategic.operationalkpi', verbose_name='شاخص‌های عملیاتی مرتبط'),
        ),
    ]
