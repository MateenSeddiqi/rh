# Generated by Django 4.0.6 on 2023-12-12 09:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rh", "0004_rename_gran_type_indicator_grant_type"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="beneficiarytype",
            name="is_regular_beneficiary",
        ),
        migrations.AlterField(
            model_name="beneficiarytype",
            name="is_hrp_beneficiary",
            field=models.BooleanField(default=False, null=True),
        ),
    ]