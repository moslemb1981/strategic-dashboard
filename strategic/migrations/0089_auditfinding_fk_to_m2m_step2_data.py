# -*- coding: utf-8 -*-
"""قدم ۲ از ۳: هر رکورد نتیجه‌ی ممیزی که قبلاً به یک ریسک/پروژه/SWOT/الزام
(تک‌ارتباطی) وصل بود رو، به فیلد جدید چندارتباطی منتقل می‌کنیم — تا هیچ
ارتباط قبلی از دست نره."""
from django.db import migrations


def copy_old_to_new(apps, schema_editor):
    AuditFinding = apps.get_model('strategic', 'AuditFinding')
    for obj in AuditFinding.objects.all():
        if obj.related_risk_old_fk_id:
            obj.related_risk.add(obj.related_risk_old_fk_id)
        if obj.related_initiative_old_fk_id:
            obj.related_initiative.add(obj.related_initiative_old_fk_id)
        if obj.related_swot_item_old_fk_id:
            obj.related_swot_item.add(obj.related_swot_item_old_fk_id)
        if obj.related_legal_requirement_old_fk_id:
            obj.related_legal_requirement.add(obj.related_legal_requirement_old_fk_id)


def noop_reverse(apps, schema_editor):
    pass  # برگشت به FK ضروری نیست — این مهاجرت فقط برای ارتقا به جلو طراحی شده


class Migration(migrations.Migration):

    dependencies = [
        ('strategic', '0088_auditfinding_fk_to_m2m_step1'),
    ]

    operations = [
        migrations.RunPython(copy_old_to_new, noop_reverse),
    ]
