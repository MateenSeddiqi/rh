# Generated by Django 4.0.6 on 2023-03-29 06:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rh', '0002_project_donors_alter_activity_activity_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='activity_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='end_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AlterField(
            model_name='activity',
            name='start_date',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]