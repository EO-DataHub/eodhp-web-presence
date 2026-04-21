"""Wagtail admin widget for picking MDI icons in StructBlock fields.

Because Wagtail's StructBlock forms are rendered client-side via Telepath,
custom widget templates and attrs are ignored — Telepath serialises the
field as a plain text input. The ``icon-field.js`` bundle finds each
``[data-contentpath="icon_name"]`` container and transforms the text input
into an icon picker at runtime.

The widget class exists solely to declare its ``Media`` so that the JS
bundle is included in the page editor via ``insert_editor_js``.
"""

from typing import ClassVar

from django import forms


class IconPickerWidget(forms.TextInput):
    """A text input that the ``icon-field.js`` bundle transforms into an icon picker."""

    class Media:
        js: ClassVar[list[str]] = ["bundles/icon-field.js"]
