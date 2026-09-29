# تبدیل کد قدیمی معاونت (group_key، رشته‌ی ثابت) به رکورد واقعی OrgUnit قابل ویرایش/افزودن/حذف.

from django.db import migrations

GROUP_DEFS = [
    ("hq", "مدیریت‌های مستقل", "ceo_direct", 0),
    ("eng", "معاونت مهندسی و کیفیت", "deputy", 1),
    ("service", "معاونت خدمات پس از فروش", "deputy", 2),
    ("biz", "معاونت توسعه کسب‌وکار و بازار", "deputy", 3),
    ("parts", "معاونت بازرگانی قطعات", "deputy", 4),
    ("log", "معاونت برنامه‌ریزی و لجستیک", "deputy", 5),
    ("fin", "معاونت مالی و اقتصادی", "deputy", 6),
    ("plan", "معاونت طرح و برنامه", "deputy", 7),
    ("hr", "معاونت توسعه منابع انسانی و پشتیبانی", "deputy", 8),
]


def forwards(apps, schema_editor):
    OrgUnit = apps.get_model("strategic", "OrgUnit")
    FunctionalStrategy = apps.get_model("strategic", "FunctionalStrategy")

    key_to_unit = {}
    for key, name, kind, order in GROUP_DEFS:
        unit, _ = OrgUnit.objects.get_or_create(name=name, defaults={"kind": kind, "order": order})
        key_to_unit[key] = unit

    for fs in FunctionalStrategy.objects.all():
        unit = key_to_unit.get(fs.group_key)
        if unit:
            fs.org_unit = unit
            fs.save(update_fields=["org_unit"])


def backwards(apps, schema_editor):
    FunctionalStrategy = apps.get_model("strategic", "FunctionalStrategy")
    for fs in FunctionalStrategy.objects.all():
        if fs.org_unit_id:
            fs.group_key = fs.org_unit.name
            fs.save(update_fields=["group_key"])


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0102_orgunit_alter_functionalstrategy_options_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
