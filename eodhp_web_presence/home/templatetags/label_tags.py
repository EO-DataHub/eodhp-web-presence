from django import template

register = template.Library()


@register.simple_tag
def unique_labels(topics: object) -> list:
    """Return deduplicated list of Label objects from a topics iterable.

    Works for both contexts:
      - TopicsGridBlock: topics is a list of StructValue (panel.labels)
      - DocumentationPage.topics: topics is a StreamField (panel.value.labels)
    """
    seen: set[str] = set()
    result: list = []
    for panel in topics:
        val = getattr(panel, "value", panel)
        labels = val.get("labels", []) if isinstance(val, dict) else getattr(val, "labels", [])
        for label in labels:
            if label is None:
                continue
            slug = label.slug if hasattr(label, "slug") else None
            if slug and slug not in seen:
                seen.add(slug)
                result.append(label)
    return result


@register.filter
def label_slugs(labels: object) -> str:
    """Return comma-separated slug list for data-labels attribute."""
    return ",".join(item.slug for item in labels if item and hasattr(item, "slug") and item.slug)
