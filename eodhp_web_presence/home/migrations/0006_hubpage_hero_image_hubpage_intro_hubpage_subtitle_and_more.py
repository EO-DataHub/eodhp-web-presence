# Generated by Django 5.0.9 on 2025-01-21 16:59

import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_homepage_aim_1_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='hubpage',
            name='hero_image',
            field=models.ImageField(blank=True, help_text='Upload a banner image (JPEG, PNG, etc.)', null=True, upload_to='hero_images/'),
        ),
        migrations.AddField(
            model_name='hubpage',
            name='intro',
            field=wagtail.fields.RichTextField(blank=True, help_text='Short paragraph below the subtitle or hero area.'),
        ),
        migrations.AddField(
            model_name='hubpage',
            name='subtitle',
            field=models.CharField(blank=True, help_text='Optional text shown below the main page title.', max_length=255),
        ),
        migrations.AlterField(
            model_name='hubpage',
            name='body',
            field=wagtail.fields.RichTextField(blank=True, help_text='Main body content.'),
        ),
    ]
