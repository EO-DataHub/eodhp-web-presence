# Generated by Django 5.0.6 on 2024-07-09 08:22

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0010_alter_newsarticlepage_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="newsarticlepage",
            old_name="date",
            new_name="post_date",
        ),
    ]