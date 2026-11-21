from django.db import migrations


def forward(apps, schema_editor):
    from django.contrib.auth.management import create_permissions
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None
    SV = apps.get_model("strategic", "SectionVisibility")
    Permission = apps.get_model("auth", "Permission")
    User = apps.get_model("auth", "User")
    Group = apps.get_model("auth", "Group")
    # دسترسی عمومی کارنامه تا امروز همان دیدبان بود؛ همان وضعیت به ردیف جدید کپی می‌شود
    src = SV.objects.filter(key="executive_show").first()
    if src and not SV.objects.filter(key="scorecard").exists():
        SV.objects.create(key="scorecard", label="کارنامه عملکرد", is_public=src.is_public)
    # هر کسی که تا امروز با دسترسی دیدبان کارنامه را می‌دید، مجوز مشاهده‌ی کارنامه را هم می‌گیرد
    new = Permission.objects.filter(content_type__app_label="strategic", codename="view_scorecardconfig").first()
    old = list(Permission.objects.filter(content_type__app_label="strategic",
               codename__in=["view_okrkeyresult", "add_okrkeyresult", "change_okrkeyresult", "delete_okrkeyresult"]))
    if new and old:
        for u in User.objects.filter(user_permissions__in=old).distinct():
            u.user_permissions.add(new)
        for g in Group.objects.filter(permissions__in=old).distinct():
            g.permissions.add(new)


class Migration(migrations.Migration):
    dependencies = [
        ("strategic", "0114_scorecard_snapshot"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]
    operations = [
        migrations.AlterModelOptions(
            name="scorecardsnapshot",
            options={"permissions": [("finalize_scorecard", "نهایی‌سازی، بازگشایی و حذف ماه کارنامه")],
                     "verbose_name": "نسخه نهایی کارنامه", "verbose_name_plural": "نسخه‌های نهایی کارنامه"},
        ),
        migrations.RunPython(forward, migrations.RunPython.noop),
    ]
