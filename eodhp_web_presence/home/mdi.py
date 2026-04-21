"""Shared validation primitives for the MDI icon feature.

Used by the Draftail exporter (`wagtail_hooks.py`), the template-time
renderer (`templatetags/mdi_tags.py`), and the server-side path lookup
(`icons.py`) so their notions of "valid" stay aligned.
"""

import re

VALID_ICON_NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

VALID_SIZES = ("sm", "md", "lg", "xl")
DEFAULT_SIZE = "sm"


def clean_name(name: object) -> str:
    if isinstance(name, str) and VALID_ICON_NAME.match(name):
        return name
    return ""


def clean_size(size: object) -> str:
    if isinstance(size, str) and size in VALID_SIZES:
        return size
    return DEFAULT_SIZE
