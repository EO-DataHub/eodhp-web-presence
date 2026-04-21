"""Template filter that injects inline SVG into MDI icon spans at render time.

Stored rich text contains ``<span data-mdi-icon="NAME" data-mdi-size="SIZE">``
placeholders. This filter replaces their contents with the appropriate inline
SVG markup looked up from ``icons.get_icon_path``, so no SVG is persisted in
the database.

The filter is idempotent: if a span already contains an ``<svg>`` child
(e.g. content saved by a previous version of the exporter), it is left
untouched.
"""

import re

from django import template
from django.utils.safestring import SafeString, mark_safe

from home.icons import get_icon_path
from home.mdi import clean_name, clean_size

register = template.Library()

_SPAN_RE = re.compile(
    r'<span\b([^>]*)data-mdi-icon=["\']([^"\']+)["\']([^>]*)>(.*?)</span>',
    re.DOTALL,
)

_ATTR_RE = re.compile(r'data-mdi-size=["\']([^"\']*)["\']')


def _inject_svg_into_span(match: re.Match) -> str:
    pre_attrs: str = match.group(1)
    name_raw: str = match.group(2)
    post_attrs: str = match.group(3)
    inner: str = match.group(4)

    name = clean_name(name_raw)
    if not name:
        return match.group(0)

    if "<svg" in inner:
        return match.group(0)

    path_d = get_icon_path(name)
    if path_d is None:
        return match.group(0)

    size_match = _ATTR_RE.search(pre_attrs + post_attrs)
    size_raw = size_match.group(1) if size_match else ""
    clean_size(size_raw)

    zwsp = "\u200b"

    svg = f'<svg viewBox="0 0 24 24" fill="currentColor"><path d="{path_d}"/></svg>'

    return f'<span{pre_attrs}data-mdi-icon="{name}"{post_attrs}>{zwsp}{svg}</span>'


@register.filter
def inject_mdi_icons(value: str) -> str:
    if not value or "data-mdi-icon" not in value:
        return value

    result = _SPAN_RE.sub(_inject_svg_into_span, value)

    if isinstance(value, SafeString):
        return mark_safe(result)
    return result
