# -*- coding: utf-8 -*-
"""قدم ۳ از ۳: حذف فیلدهای موقت قدیمی (چون داده‌شون در قدم قبلی به فیلدهای
جدید چندارتباطی منتقل شد و دیگر نیازی به نسخه‌ی قدیمی نیست)."""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('strategic', '0089_auditfinding_fk_to_m2m_step2_data'),
    ]

    operations = [
        migrations.RemoveField(model_name='auditfinding', name='related_risk_old_fk'),
        migrations.RemoveField(model_name='auditfinding', name='related_initiative_old_fk'),
        migrations.RemoveField(model_name='auditfinding', name='related_swot_item_old_fk'),
        migrations.RemoveField(model_name='auditfinding', name='related_legal_requirement_old_fk'),
    ]
