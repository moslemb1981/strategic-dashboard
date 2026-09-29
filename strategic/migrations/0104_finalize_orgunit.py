import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("strategic", "0103_migrate_group_key_to_orgunit"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="functionalstrategy",
            name="group_key",
        ),
        migrations.AlterField(
            model_name="functionalstrategy",
            name="org_unit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="functional_strategies",
                to="strategic.orgunit",
                verbose_name="معاونت / واحد سازمانی",
            ),
        ),
    ]
