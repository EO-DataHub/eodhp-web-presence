from django import template

register = template.Library()


@register.simple_tag
def bg_classes(color: str, full_width: bool = False) -> str:
    """Return background utility classes for a theme color.

    Treats blank and 'default' values as no-background, and only adds
    ``bg-full-width`` when a valid colour is present.
    """
    if not color or color == "default":
        return ""
    classes = f"bg--{color}"
    if full_width:
        classes += " bg-full-width"
    return classes
