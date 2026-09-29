from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0104_finalize_orgunit"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="functionalstrategy",
            name="business_units",
        ),
    ]
