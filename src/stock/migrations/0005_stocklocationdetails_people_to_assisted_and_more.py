# Generated by Django 4.0.6 on 2024-04-29 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0004_rename_status_stockreports_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='stocklocationdetails',
            name='people_to_assisted',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='No People to be assisted'),
        ),
        migrations.AddField(
            model_name='stocklocationdetails',
            name='unit_required',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='No Unit Required'),
        ),
    ]
