# Generated by Django 5.0.4 on 2024-06-28 14:11

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0005_homepage_about_image_homepage_contact_image_and_more"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="AnnouncementPage",
            new_name="NewsArticlePage",
        ),
        migrations.RenameModel(
            old_name="AnnouncementsPage",
            new_name="NewsPage",
        ),
    ]
