"""Template filter and tags for MDI icon rendering.

``inject_mdi_icons`` filter — replaces ``<span data-mdi-icon="NAME">``
placeholders in stored rich text with inline SVG at render time.

``{% mdi_icon name [size] %}`` tag — outputs a fully-rendered inline SVG
icon directly, for use in block templates where icon_name / icon_size are
explicit StructBlock field values.
"""

import re

from django import template
from django.utils.safestring import SafeString, mark_safe

from home.icons import get_icon_path
from home.mdi import DEFAULT_SIZE, clean_name, clean_size

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


@register.simple_tag
def mdi_icon(name: str, size: str = DEFAULT_SIZE) -> str:
    """Render an MDI icon as an inline SVG ``<span>`` directly.

    Usage::

        {% load mdi_tags %}
        {% mdi_icon "account" "md" %}
        {% mdi_icon "rocket-launch" %}       {# size defaults to "sm" #}

    Returns a ``<span class="mdi" data-mdi-icon="NAME" data-mdi-size="SIZE">``
    containing the inline SVG. If *name* is invalid or unknown, returns an
    empty string.
    """
    clean = clean_name(name)
    if not clean:
        return ""

    path_d = get_icon_path(clean)
    if path_d is None:
        return ""

    sz = clean_size(size) if size else DEFAULT_SIZE
    svg = f'<svg viewBox="0 0 24 24" fill="currentColor"><path d="{path_d}"/></svg>'
    return mark_safe(
        f'<span class="mdi mdi-{clean}" aria-hidden="true" data-mdi-icon="{clean}" data-mdi-size="{sz}">{svg}</span>'
    )
