# Generated by Django 5.0.4 on 2024-06-28 13:17

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0004_announcementspage_contactpage_homepage_image_and_more"),
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="about_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="contact_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="news_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Landscape mode only; horizontal width between 1000px and 3000px.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]
