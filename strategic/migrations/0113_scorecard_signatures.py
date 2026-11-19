from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("strategic", "0112_scorecard")]
    operations = [
        migrations.AddField(
            model_name="scorecardconfig",
            name="signatures",
            field=models.TextField(blank=True, default="", verbose_name="امضاها (JSON: عنوان، سمت، نام)"),
        ),
    ]
