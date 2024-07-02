# Generated by Django 5.0.4 on 2024-07-02 09:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("home", "0010_helpareapage_helpfaqpage_helpindexpage_helptopicpage"),
        ("wagtailcore", "0089_log_entry_data_json_null_to_object"),
        ("wagtailimages", "0025_alter_image_file_alter_rendition_file"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="HelpAreaPage",
            new_name="SupportAreaPage",
        ),
        migrations.RenameModel(
            old_name="HelpFAQPage",
            new_name="SupportFAQPage",
        ),
        migrations.RenameModel(
            old_name="HelpIndexPage",
            new_name="SupportIndexPage",
        ),
        migrations.RenameModel(
            old_name="HelpTopicPage",
            new_name="SupportTopicPage",
        ),
    ]
