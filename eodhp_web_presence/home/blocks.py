from wagtail import blocks
from wagtail.blocks.struct_block import BlockGroup
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtail.snippets.blocks import SnippetChooserBlock
from wagtailcodeblock.blocks import CodeBlock

from .colors import THEME_COLOR_CHOICES
from .mdi import VALID_SIZES
from .widgets import IconPickerWidget

WIDTH_CHOICES = [
    ("default", "Default"),
    ("medium", "Medium"),
    ("small", "Small"),
]

ALIGNMENT_CHOICES = [
    ("none", "None"),
    ("left", "Left"),
    ("centre", "Centre"),
    ("right", "Right"),
]

VERTICAL_ALIGNMENT_CHOICES = [
    ("top", "Top"),
    ("centre", "Centre"),
    ("bottom", "Bottom"),
]

IMAGE_WIDTH_CHOICES = [
    ("100", "Original dimensions (100%)"),
    ("75", "75% of original dimensions"),
    ("50", "50% of original dimensions"),
    ("25", "25% of original dimensions"),
]

IMAGE_STYLE_CHOICES = [
    ("rounded", "Rounded corners"),
    ("square", "Square corners"),
    ("pill", "Pill / circular"),
]

BUTTON_STYLE_CHOICES = [
    ("primary", "Primary"),
    ("secondary", "Secondary"),
]

FONT_SIZE_CHOICES = [
    ("default", "Default"),
    ("small", "Small"),
    ("large", "Large"),
]

FONT_WEIGHT_CHOICES = [
    ("normal", "Normal"),
    ("bold", "Bold"),
]

FONT_STYLE_CHOICES = [
    ("italic", "Italic"),
    ("normal", "Normal"),
]

# ── Reusable form-layout field lists & group helpers ──────────────────
LAYOUT_FIELDS = ["width", "alignment", "vertical_alignment"]
BACKGROUND_FIELDS = ["background_color", "full_width_background"]
FONT_FIELDS = ["font_size", "font_weight", "font_style"]

ICON_SIZE_CHOICES = [(s, s.upper()) for s in VALID_SIZES]

ICON_FIELDS = ["icon_name", "icon_size"]


def _icon_group() -> BlockGroup:
    return BlockGroup(ICON_FIELDS, heading="Icon", icon="snippet", classname="collapsed")


def _layout_group() -> BlockGroup:
    return BlockGroup(LAYOUT_FIELDS, heading="Layout", icon="sliders", classname="collapsed")


def _background_group() -> BlockGroup:
    return BlockGroup(BACKGROUND_FIELDS, heading="Background", icon="cog", classname="collapsed")


def _font_group() -> BlockGroup:
    return BlockGroup(FONT_FIELDS, heading="Typography", icon="bold", classname="collapsed")


def _image_options_group(*extra_fields: str) -> BlockGroup:
    """Image styling fields. Pass extra field names for block-specific additions."""
    fields = ["image_width", "image_style"] + list(extra_fields)
    return BlockGroup(fields, heading="Image Options", icon="image", classname="collapsed")


def _image_link_group() -> BlockGroup:
    return BlockGroup(["image_link_page", "image_link_url"], heading="Image Link", icon="link", classname="collapsed")


class FontMixin(blocks.StructBlock):
    """Reusable font options — inherit from this for typography control."""

    font_size = blocks.ChoiceBlock(
        choices=FONT_SIZE_CHOICES,
        default="default",
        required=False,
        help_text="Font size for this block.",
    )
    font_weight = blocks.ChoiceBlock(
        choices=FONT_WEIGHT_CHOICES,
        default="normal",
        required=False,
        help_text="Font weight for this block.",
    )
    font_style = blocks.ChoiceBlock(
        choices=FONT_STYLE_CHOICES,
        default="normal",
        required=False,
        help_text="Font style for this block.",
    )


class LayoutMixin(blocks.StructBlock):
    """Reusable layout options — inherit from this instead of StructBlock."""

    width = blocks.ChoiceBlock(
        choices=WIDTH_CHOICES,
        default="default",
        required=False,
        help_text="Control how wide this block spans.",
    )
    alignment = blocks.ChoiceBlock(
        choices=ALIGNMENT_CHOICES,
        default="none",
        required=False,
        help_text="Horizontal alignment within the page.",
    )
    vertical_alignment = blocks.ChoiceBlock(
        choices=VERTICAL_ALIGNMENT_CHOICES,
        default="top",
        required=False,
        help_text="Vertical alignment within a column layout.",
    )


class BackgroundMixin(blocks.StructBlock):
    """Reusable background color option."""

    background_color = blocks.ChoiceBlock(
        choices=THEME_COLOR_CHOICES,
        default="default",
        required=False,
        help_text="Background color for this block.",
    )
    full_width_background = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Stretch the background to the full width of the page.",
    )


class IconPickerBlock(blocks.CharBlock):
    """CharBlock whose form field uses the MDI icon picker widget."""

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self.field.widget = IconPickerWidget()


class IconMixin(blocks.StructBlock):
    """Reusable icon options — inherit from this to add an icon beside a heading/title."""

    icon_name = IconPickerBlock(
        required=False,
        max_length=100,
        help_text="Click the Pick icon button to browse available icons.",
    )
    icon_size = blocks.ChoiceBlock(
        choices=ICON_SIZE_CHOICES,
        default="sm",
        required=False,
        help_text="Icon size.",
    )


class ContentBlock(IconMixin, LayoutMixin, BackgroundMixin):
    heading = blocks.CharBlock(required=False, help_text="Optional heading")
    paragraph = blocks.RichTextBlock(required=False)
    image = ImageChooserBlock(required=False)
    image_link_page = blocks.PageChooserBlock(
        required=False,
        help_text="Link the image to an internal page.",
    )
    image_link_url = blocks.URLBlock(
        required=False,
        help_text="Link the image to an external URL. Page link takes priority if both are set.",
    )
    image_width = blocks.ChoiceBlock(
        choices=IMAGE_WIDTH_CHOICES,
        default="100",
        required=False,
        help_text="Display width as a percentage of the image's original dimensions.",
    )
    image_style = blocks.ChoiceBlock(
        choices=IMAGE_STYLE_CHOICES,
        default="rounded",
        required=False,
        help_text="Visual style for the image.",
    )
    image_alignment = blocks.ChoiceBlock(
        choices=ALIGNMENT_CHOICES,
        default="centre",
        required=False,
        help_text="Horizontal alignment of the image within the block.",
    )

    class Meta:
        icon = "doc-full"
        label = "Content Block"
        template = "blocks/content_block.html"
        help_text = "Use this block to create flexible content sections."
        form_layout = BlockGroup(
            children=["heading", "paragraph", "image"],
            settings=[
                _icon_group(),
                _image_link_group(),
                _image_options_group("image_alignment"),
                _layout_group(),
                _background_group(),
            ],
        )


class ImageBlock(LayoutMixin, BackgroundMixin):
    """Standalone image block — lightweight alternative to ContentBlock for columns."""

    image = ImageChooserBlock(required=True)
    image_link_page = blocks.PageChooserBlock(
        required=False,
        help_text="Link the image to an internal page.",
    )
    image_link_url = blocks.URLBlock(
        required=False,
        help_text="Link the image to an external URL. Page link takes priority if both are set.",
    )
    image_width = blocks.ChoiceBlock(
        choices=IMAGE_WIDTH_CHOICES,
        default="100",
        required=False,
        help_text="Display width as a percentage of the image's original dimensions.",
    )
    image_style = blocks.ChoiceBlock(
        choices=IMAGE_STYLE_CHOICES,
        default="rounded",
        required=False,
        help_text="Visual style for the image.",
    )

    class Meta:
        icon = "image"
        label = "Image"
        template = "blocks/image_block.html"
        help_text = "A standalone image with optional link and styling."
        form_layout = BlockGroup(
            children=["image"],
            settings=[
                _image_link_group(),
                _image_options_group(),
                _layout_group(),
                _background_group(),
            ],
        )


class AccordionItemBlock(IconMixin, blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Accordion item heading")
    content = blocks.RichTextBlock(required=True, help_text="Content revealed when expanded")

    class Meta:
        icon = "collapse-down"
        label = "Accordion Item"
        form_layout = BlockGroup(
            children=["title", "content"],
            settings=[
                _icon_group(),
            ],
        )


class AccordionBlock(LayoutMixin, BackgroundMixin):
    header_color = blocks.ChoiceBlock(
        choices=THEME_COLOR_CHOICES,
        default="default",
        required=False,
        help_text="Background color for accordion headers.",
    )
    content_color = blocks.ChoiceBlock(
        choices=THEME_COLOR_CHOICES,
        default="default",
        required=False,
        help_text="Background color for accordion content panels.",
    )
    items = blocks.ListBlock(AccordionItemBlock())

    class Meta:
        icon = "collapse-down"
        label = "Accordion"
        template = "blocks/accordion_block.html"
        help_text = "A set of collapsible content sections."
        form_layout = BlockGroup(
            children=["items"],
            settings=[
                BlockGroup(["header_color", "content_color"], heading="Colors", icon="cogs", classname="collapsed"),
                _layout_group(),
                _background_group(),
            ],
        )


class MediaEmbedBlock(LayoutMixin, BackgroundMixin):
    url = EmbedBlock(help_text="Paste a URL to embed (YouTube, Vimeo, Spotify, etc.).")
    caption = blocks.CharBlock(required=False, help_text="Optional caption below the embed.")

    class Meta:
        icon = "media"
        label = "Embed"
        template = "blocks/embed_block.html"
        help_text = "Embed content from YouTube, Vimeo, Spotify, and other providers."
        form_layout = BlockGroup(
            children=["url", "caption"],
            settings=[
                _layout_group(),
                _background_group(),
            ],
        )


class QuoteBlock(IconMixin, LayoutMixin, BackgroundMixin, FontMixin):
    """A styled blockquote with layout, background, and font options."""

    # Override BackgroundMixin default — quotes get a background by default.
    background_color = blocks.ChoiceBlock(
        choices=THEME_COLOR_CHOICES,
        default="light-grey",
        required=False,
        help_text="Background color for this block.",
    )

    # Override FontMixin default — quotes are italic by default.
    font_style = blocks.ChoiceBlock(
        choices=FONT_STYLE_CHOICES,
        default="italic",
        required=False,
        help_text="Font style for this block.",
    )

    quote = blocks.TextBlock(
        required=True,
        help_text="The quote text.",
    )
    attribution = blocks.CharBlock(
        required=False,
        help_text="Optional attribution (e.g., author name).",
    )

    class Meta:
        icon = "openquote"
        label = "Quote"
        template = "blocks/quote_block.html"
        form_layout = BlockGroup(
            children=["quote", "attribution"],
            settings=[
                _icon_group(),
                _font_group(),
                _layout_group(),
                _background_group(),
            ],
        )


class CTABlock(LayoutMixin, BackgroundMixin):
    text = blocks.CharBlock(required=True, help_text="Button label text")
    link_page = blocks.PageChooserBlock(
        required=False,
        help_text="Link to an internal page. Takes priority over the URL field if both are set.",
    )
    link_url = blocks.URLBlock(
        required=False,
        help_text="Link to an external URL.",
    )
    button_style = blocks.ChoiceBlock(
        choices=BUTTON_STYLE_CHOICES,
        default="primary",
        required=False,
        help_text="Visual style for the button.",
    )

    class Meta:
        icon = "link"
        label = "Call to Action"
        template = "blocks/cta_block.html"
        help_text = "A call-to-action button or link."
        form_layout = BlockGroup(
            children=["text", "link_page", "link_url"],
            settings=[
                BlockGroup(["button_style"], heading="Style", icon="tag", classname="collapsed"),
                _layout_group(),
                _background_group(),
            ],
        )


class DocumentationPanel(IconMixin, blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Title of the documentation panel")
    slug = blocks.CharBlock(
        required=True,
        help_text="Unique identifier in the url e.g. workflow",
        max_length=50,
    )
    description = blocks.RichTextBlock(required=True, help_text="Description of the documentation panel")
    image = ImageChooserBlock(required=False, help_text="Optional image for the documentation panel")
    featured_image = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Use the image as a full card background with the title overlaid",
    )
    labels = blocks.ListBlock(
        SnippetChooserBlock("home.Label"),
        required=False,
        label="Labels",
        default=[],
    )

    class Meta:
        icon = "doc-full"
        label = "Documentation Panel"
        template = "blocks/documentation_panel.html"
        help_text = "Use this block to create documentation panels with title, description, and optional image."
        form_layout = BlockGroup(
            children=["title", "slug", "labels", "description", "image", "featured_image"],
            settings=[
                _icon_group(),
            ],
        )


COLUMN_LAYOUT_CHOICES = [
    ("1-1", "Two columns (50 / 50)"),
    ("1-2", "Two columns (33 / 67)"),
    ("2-1", "Two columns (67 / 33)"),
    ("1-1-1", "Three columns (33 / 33 / 33)"),
    ("1-1-1-1", "Four columns (25 / 25 / 25 / 25)"),
    ("1-2-1", "Three columns (25 / 50 / 25)"),
]


# Helper: blocks allowed inside columns (no nesting of rows)
def _inner_blocks() -> list:
    return [
        ("content_block", ContentBlock()),
        ("image", ImageBlock()),
        ("accordion", AccordionBlock()),
        ("embed", MediaEmbedBlock()),
        ("blockquote", QuoteBlock()),
        ("raw_html", blocks.RawHTMLBlock()),
        ("code", CodeBlock(label="Code")),
        ("cta", CTABlock()),
    ]


class ColumnBlock(BackgroundMixin):
    # Columns live inside a RowBlock grid — full-width breakout would escape
    # the grid cell, so we hide the option from editors.
    full_width_background = None

    stretch = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Stretch text content to fill the full column height.",
    )
    content = blocks.StreamBlock(_inner_blocks())

    class Meta:
        icon = "placeholder"
        label = "Column"
        template = "blocks/column_block.html"
        form_layout = BlockGroup(
            children=["content"],
            settings=[
                BlockGroup(["stretch", "background_color"], heading="Options", icon="cog", classname="collapsed"),
            ],
        )


class RowBlock(BackgroundMixin):
    layout = blocks.ChoiceBlock(
        choices=COLUMN_LAYOUT_CHOICES,
        default="1-1",
        help_text="Choose a column layout for this row.",
    )
    columns = blocks.ListBlock(ColumnBlock(), min_num=1, max_num=4)

    class Meta:
        icon = "grip"
        label = "Columns"
        template = "blocks/row_block.html"
        help_text = "Arrange content in side-by-side columns."
        form_layout = BlockGroup(
            children=["layout", "columns"],
            settings=[
                _background_group(),
            ],
        )


class TopicsGridBlock(BackgroundMixin):
    """A grid of topic / documentation cards"""

    topics = blocks.ListBlock(DocumentationPanel(), label="Topic cards")
    show_filter = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Show a label filter bar above the topic cards.",
    )

    class Meta:
        icon = "grip"
        label = "Topics Grid"
        template = "blocks/topics_grid_block.html"
        help_text = "A grid of topic / documentation cards."
        form_layout = BlockGroup(
            children=["topics"],
            settings=[
                BlockGroup(["show_filter"], heading="Filter", icon="tag", classname="collapsed"),
                _background_group(),
            ],
        )


# Helper: StreamField definitions shared by landing / index pages
def _body_blocks() -> list:
    return _inner_blocks() + [
        ("columns", RowBlock()),
        ("topics_grid", TopicsGridBlock()),
    ]
