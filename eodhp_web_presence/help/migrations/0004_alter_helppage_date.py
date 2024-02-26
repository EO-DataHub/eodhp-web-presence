# Generated by Django 5.0.1 on 2024-02-19 13:18

import datetime

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("help", "0003_remove_helpindexpage_date_published_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="helppage",
            name="date",
            field=models.DateField(
                blank=True, default=datetime.date.today, null=True, verbose_name="Date"
            ),
        ),
    ]