from django import template
from wagtail.images import get_image_model

register = template.Library()

ImageModel = get_image_model()


@register.inclusion_tag("includes/pictures/content_image.html")
def content_picture(image: ImageModel) -> dict[str, ImageModel]:
    return {"image": image}


@register.inclusion_tag("includes/pictures/hero_image.html")
def hero_picture(image: ImageModel) -> dict[str, ImageModel]:
    return {"image": image}


@register.inclusion_tag("includes/pictures/featured_card_image.html")
def featured_card_picture(image: ImageModel) -> dict[str, ImageModel]:
    return {"image": image}


@register.inclusion_tag("includes/pictures/thumb_image.html")
def thumb_picture(image: ImageModel) -> dict[str, ImageModel]:
    return {"image": image}
