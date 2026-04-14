from django.templatetags.static import static
from django.utils.html import format_html
from wagtail import hooks
from wagtail.admin.rich_text.converters.html_to_contentstate import (
    BlockElementHandler,
)
from wagtail.admin.rich_text.editors.draftail import features as draftail_features
from wagtail.rich_text.feature_registry import FeatureRegistry


# ── Admin branding & preview CSS ───────────────────────────────────────
@hooks.register("insert_global_admin_css")
def admin_extra_css() -> str:
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("core/css/admin-extra.css"),
    )


# ── Rich text: enable additional built-in features by default ──────────
@hooks.register("register_rich_text_features")
def register_extra_default_features(features: FeatureRegistry) -> None:
    features.default_features.extend(
        [
            "blockquote",
            "superscript",
            "subscript",
            "strikethrough",
            "code",
        ]
    )


# ── Rich text: custom "callout" block feature ─────────────────────────
@hooks.register("register_rich_text_features")
def register_callout_feature(features: FeatureRegistry) -> None:
    feature_name = "callout"

    features.register_editor_plugin(
        "draftail",
        feature_name,
        draftail_features.BlockFeature(
            {
                "type": "callout",
                "icon": "info-circle",
                "description": "Callout",
            }
        ),
    )

    features.register_converter_rule(
        "contentstate",
        feature_name,
        {
            "from_database_format": {
                'div[class="callout"]': BlockElementHandler("callout"),
            },
            "to_database_format": {
                "block_map": {
                    "callout": {
                        "element": "div",
                        "props": {"class": "callout"},
                    }
                }
            },
        },
    )

    features.default_features.append(feature_name)
