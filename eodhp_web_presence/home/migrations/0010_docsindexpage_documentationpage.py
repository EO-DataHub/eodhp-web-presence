# Generated by Django 5.0.9 on 2025-01-29 15:49

import django.db.models.deletion
import wagtail.blocks
import wagtail.fields
import wagtail.images.blocks
import wagtailcache.cache
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_remove_documentationpage_page_ptr_and_more'),
        ('wagtailcore', '0089_log_entry_data_json_null_to_object'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocsIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro', wagtail.fields.RichTextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtailcache.cache.WagtailCacheMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='DocumentationPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.page')),
                ('intro', wagtail.fields.RichTextField(blank=True)),
                ('topics', wagtail.fields.StreamField([('documentation_panel', wagtail.blocks.StructBlock([('title', wagtail.blocks.CharBlock(help_text='Title of the documentation panel', required=True)), ('slug', wagtail.blocks.CharBlock(help_text='Unique identifier in the url e.g. workflow', max_length=50, required=True)), ('description', wagtail.blocks.RichTextBlock(help_text='Description of the documentation panel', required=True)), ('image', wagtail.images.blocks.ImageChooserBlock(help_text='Optional image for the documentation panel', required=False))]))], blank=True, help_text='Add documentation panels to this page.', use_json_field=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(wagtailcache.cache.WagtailCacheMixin, 'wagtailcore.page'),
        ),
    ]
