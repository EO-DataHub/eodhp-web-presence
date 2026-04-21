"""Rich-text extensions for the `home` app.

Registers a Draftail inline entity that lets editors insert Material Design
Icons (https://pictogrammers.com/library/mdi/) anywhere rich text is edited,
with UX modelled on the existing emoji copy-paste workflow.
"""

from draftjs_exporter.dom import DOM, Element
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    InlineEntityElementHandler,
)
from wagtail.admin.rich_text.editors.draftail import features as draftail_features
from wagtail.rich_text.feature_registry import FeatureRegistry

from .mdi import clean_name, clean_size

ICON_FEATURE_NAME = "icon"
ICON_ENTITY_TYPE = "ICON"


def icon_entity(props: dict) -> Element:
    """Serialize an ICON entity to the HTML we persist in the database.

    Output shape: <span class="mdi mdi-NAME" aria-hidden="true"
                        data-mdi-icon="NAME" data-mdi-size="SIZE">
                    &#x200b;
                  </span>

    SVG markup is *not* baked into stored HTML. Instead, the
    ``inject_mdi_icons`` template filter (see ``templatetags/mdi_tags.py``)
    inserts inline SVG at render time using ``icons.get_icon_path``.
    This keeps the database free of presentation markup and means icon
    updates take effect without re-saving any pages.

    The ``data-mdi-icon`` / ``data-mdi-size`` attributes are kept on the
    span so the admin-side ElementHandler can parse the entity back when
    the page is re-edited, and so the template filter can look up the SVG
    path at render time.

    Size is driven off the ``data-mdi-size`` attribute (see
    ``mdi_icon.scss`) -- never a CSS class, because MDI ships real icons
    literally named ``size-sm`` / ``size-md`` / ``size-xl`` etc. and a
    ``mdi-size-*`` class would render the letter-in-a-box glyph instead
    of resizing anything.
    """
    name = clean_name(props.get("name"))
    size = clean_size(props.get("size"))
    children = props.get("children", "")
    span_attrs = {
        "class": f"mdi mdi-{name}" if name else "mdi",
        "aria-hidden": "true",
        "data-mdi-icon": name,
        "data-mdi-size": size,
    }
    return DOM.create_element("span", span_attrs, children)


class IconEntityElementHandler(InlineEntityElementHandler):
    """Parse a stored <span data-mdi-icon="..."> back into an ICON entity."""

    mutability = "IMMUTABLE"

    def get_attribute_data(self, attrs: dict[str, str]) -> dict[str, str]:
        return {
            "name": clean_name(attrs.get("data-mdi-icon", "")),
            "size": clean_size(attrs.get("data-mdi-size", "")),
        }


@hooks.register("register_rich_text_features")
def register_icon_feature(features: FeatureRegistry) -> None:
    features.register_editor_plugin(
        "draftail",
        ICON_FEATURE_NAME,
        draftail_features.EntityFeature(
            {
                "type": ICON_ENTITY_TYPE,
                "description": "Insert a Material Design icon",
                "icon": "snippet",
            },
            js=["bundles/icon-picker.js"],
        ),
    )

    features.register_converter_rule(
        "contentstate",
        ICON_FEATURE_NAME,
        {
            "from_database_format": {
                "span[data-mdi-icon]": IconEntityElementHandler(ICON_ENTITY_TYPE),
            },
            "to_database_format": {
                "entity_decorators": {ICON_ENTITY_TYPE: icon_entity},
            },
        },
    )

    features.default_features.append(ICON_FEATURE_NAME)
