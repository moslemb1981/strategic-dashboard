from django.db import migrations

OLD_TO_NEW = {
    "on_track": "in_progress",
    "needs_attention": "deviation",
    "digital": "in_progress",
}


def migrate_statuses_forward(apps, schema_editor):
    Initiative = apps.get_model("strategic", "Initiative")
    for old_value, new_value in OLD_TO_NEW.items():
        Initiative.objects.filter(status=old_value).update(status=new_value)


def migrate_statuses_backward(apps, schema_editor):
    # برگشت دقیق ممکن نیست چون چند وضعیت قدیمی به یک وضعیت جدید نگاشت شده‌اند؛ بدون تغییر رها می‌شود.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0073_initiative_code_alter_initiative_status"),
    ]

    operations = [
        migrations.RunPython(migrate_statuses_forward, migrate_statuses_backward),
    ]
