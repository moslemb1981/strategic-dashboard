from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("strategic", "0115_scorecard_permissions")]
    operations = [
        migrations.AddField(
            model_name="scorecardconfig",
            name="use_org_score",
            field=models.BooleanField(default=True, verbose_name="ردیف «امتیاز اهداف سازمان (شرکت مادر)» در کارنامه حساب شود"),
        ),
    ]
