# Generated by Django 5.0.6 on 2024-07-03 13:22

import django.db.models.deletion
import wagtailcache.cache
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0004_announcementspage_contactpage_homepage_image_and_more"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AnnouncementPage",
            new_name="NewsArticlePage",
        ),
        migrations.AddField(
            model_name="aboutpage",
            name="banner_image",
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
            model_name="contactpage",
            name="banner_image",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
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
            name="banner_image",
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
        migrations.CreateModel(
            name="NewsPage",
            fields=[
                (
                    "page_ptr",
                    models.OneToOneField(
                        auto_created=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        serialize=False,
                        to="wagtailcore.page",
                    ),
                ),
                (
                    "banner_image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="wagtailimages.image",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
            bases=(wagtailcache.cache.WagtailCacheMixin, "wagtailcore.page"),
        ),
        migrations.DeleteModel(
            name="AnnouncementsPage",
        ),
    ]
