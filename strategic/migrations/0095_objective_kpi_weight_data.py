# -*- coding: utf-8 -*-
"""افزودن وزن به شاخص‌های هر کارت هدف استراتژیک — قدم ۲ از ۳.
برای تمام ارتباط‌های (هدف، شاخص) که همین الان در سیستم برقرار هستند، یک رکورد وزن
با مقدار ۱۰۰ ساخته می‌شود تا محاسبات فعلی (میانگین ساده) دقیقاً همان‌طور که تا الان
بوده ادامه پیدا کند — هیچ داده‌ای گم یا صفر نمی‌شود."""
from django.db import migrations


def copy_weights_forward(apps, schema_editor):
    StrategicObjective = apps.get_model('strategic', 'StrategicObjective')
    ObjectiveKPIWeight = apps.get_model('strategic', 'ObjectiveKPIWeight')
    ObjectiveOperationalKPIWeight = apps.get_model('strategic', 'ObjectiveOperationalKPIWeight')

    kpi_rows = []
    for obj in StrategicObjective.objects.all():
        for kpi in obj.linked_kpis.all():
            kpi_rows.append(ObjectiveKPIWeight(objective_id=obj.pk, kpi_id=kpi.pk, weight=100))
    if kpi_rows:
        ObjectiveKPIWeight.objects.bulk_create(kpi_rows, ignore_conflicts=True)

    opkpi_rows = []
    for obj in StrategicObjective.objects.all():
        for kpi in obj.linked_operational_kpis.all():
            opkpi_rows.append(ObjectiveOperationalKPIWeight(objective_id=obj.pk, kpi_id=kpi.pk, weight=100))
    if opkpi_rows:
        ObjectiveOperationalKPIWeight.objects.bulk_create(opkpi_rows, ignore_conflicts=True)


def copy_weights_backward(apps, schema_editor):
    ObjectiveKPIWeight = apps.get_model('strategic', 'ObjectiveKPIWeight')
    ObjectiveOperationalKPIWeight = apps.get_model('strategic', 'ObjectiveOperationalKPIWeight')
    ObjectiveKPIWeight.objects.all().delete()
    ObjectiveOperationalKPIWeight.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('strategic', '0094_objective_kpi_weight_tables'),
    ]

    operations = [
        migrations.RunPython(copy_weights_forward, copy_weights_backward),
    ]
