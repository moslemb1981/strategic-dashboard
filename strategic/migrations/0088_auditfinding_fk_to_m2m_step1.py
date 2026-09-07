# -*- coding: utf-8 -*-
"""تبدیل ۴ فیلد تک‌ارتباطی (ForeignKey) نتایج ممیزی به چندارتباطی (ManyToMany).
قدم ۱ از ۳: نام فیلدهای قدیمی رو موقتاً عوض می‌کنیم (بدون حذف داده) و فیلدهای
جدید M2M رو با همون نام اصلی اضافه می‌کنیم. قدم بعدی (migration بعدی) داده‌های
قدیمی رو به فیلدهای جدید منتقل می‌کنه؛ قدم آخر فیلدهای موقت رو حذف می‌کنه.
"""
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('strategic', '0087_auditfinding_related_initiative_and_more'),
    ]

    operations = [
        migrations.RenameField(model_name='auditfinding', old_name='related_risk', new_name='related_risk_old_fk'),
        migrations.RenameField(model_name='auditfinding', old_name='related_initiative', new_name='related_initiative_old_fk'),
        migrations.RenameField(model_name='auditfinding', old_name='related_swot_item', new_name='related_swot_item_old_fk'),
        migrations.RenameField(model_name='auditfinding', old_name='related_legal_requirement', new_name='related_legal_requirement_old_fk'),
        migrations.AlterField(
            model_name='auditfinding', name='related_risk_old_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_findings_old', to='strategic.risk'),
        ),
        migrations.AlterField(
            model_name='auditfinding', name='related_initiative_old_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_findings_old', to='strategic.initiative'),
        ),
        migrations.AlterField(
            model_name='auditfinding', name='related_swot_item_old_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_findings_old', to='strategic.swotitem'),
        ),
        migrations.AlterField(
            model_name='auditfinding', name='related_legal_requirement_old_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_findings_old', to='strategic.legalrequirement'),
        ),
        migrations.AddField(
            model_name='auditfinding', name='related_risk',
            field=models.ManyToManyField(blank=True, related_name='audit_findings', to='strategic.risk', verbose_name='ریسک\\u200cهای مرتبط (اختیاری)'),
        ),
        migrations.AddField(
            model_name='auditfinding', name='related_initiative',
            field=models.ManyToManyField(blank=True, related_name='audit_findings', to='strategic.initiative', verbose_name='پروژه\\u200cها/اقدامات اصلاحی مرتبط (اختیاری)'),
        ),
        migrations.AddField(
            model_name='auditfinding', name='related_swot_item',
            field=models.ManyToManyField(blank=True, limit_choices_to={'category': 'w'}, related_name='audit_findings', to='strategic.swotitem', verbose_name='نقاط\\u200cضعف SWOT مرتبط (اختیاری)'),
        ),
        migrations.AddField(
            model_name='auditfinding', name='related_legal_requirement',
            field=models.ManyToManyField(blank=True, related_name='audit_findings', to='strategic.legalrequirement', verbose_name='الزامات قانونی مرتبط (اختیاری)'),
        ),
    ]
