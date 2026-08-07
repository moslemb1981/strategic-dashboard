# -*- coding: utf-8 -*-
from django.db import migrations


def copy_old_relations(apps, schema_editor):
    Stakeholder = apps.get_model("strategic", "Stakeholder")
    for sh in Stakeholder.objects.exclude(related_porter__isnull=True):
        sh.related_porters.add(sh.related_porter_id)


def reverse_noop(apps, schema_editor):
    # برگشت لازم نیست؛ داده در فیلد قدیمی هنوز دست‌نخورده باقی می‌ماند تا حذف نهایی در migration بعدی.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0055_stakeholder_related_porters"),
    ]

    operations = [
        migrations.RunPython(copy_old_relations, reverse_noop),
    ]
