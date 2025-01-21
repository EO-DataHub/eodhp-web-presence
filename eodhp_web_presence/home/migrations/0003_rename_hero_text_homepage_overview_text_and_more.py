# Generated by Django 5.0.9 on 2025-01-21 16:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_rename_body_homepage_hero_text_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='homepage',
            old_name='hero_text',
            new_name='overview_text',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='hero_image',
        ),
        migrations.RemoveField(
            model_name='homepage',
            name='overview',
        ),
    ]
