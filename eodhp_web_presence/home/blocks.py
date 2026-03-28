from wagtail import blocks
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
from wagtailcodeblock.blocks import CodeBlock

from .colors import THEME_COLOR_CHOICES

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
    ("100", "Full width (100%)"),
    ("75", "Three-quarters (75%)"),
    ("50", "Half (50%)"),
    ("25", "Quarter (25%)"),
]

IMAGE_STYLE_CHOICES = [
    ("rounded", "Rounded corners"),
    ("square", "Square corners"),
    ("pill", "Pill / circular"),
]


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


class ContentBlock(LayoutMixin, BackgroundMixin):
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
        help_text="Control the display width of the image.",
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
        help_text="Control the display width of the image.",
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


class AccordionItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True, help_text="Accordion item heading")
    content = blocks.RichTextBlock(required=True, help_text="Content revealed when expanded")

    class Meta:
        icon = "collapse-down"
        label = "Accordion Item"


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


class MediaEmbedBlock(LayoutMixin, BackgroundMixin):
    url = EmbedBlock(help_text="Paste a URL to embed (YouTube, Vimeo, Spotify, etc.).")
    caption = blocks.CharBlock(required=False, help_text="Optional caption below the embed.")

    class Meta:
        icon = "media"
        label = "Embed"
        template = "blocks/embed_block.html"
        help_text = "Embed content from YouTube, Vimeo, Spotify, and other providers."


class DocumentationPanel(blocks.StructBlock):
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

    class Meta:
        icon = "doc-full"
        label = "Documentation Panel"
        template = "blocks/documentation_panel.html"
        help_text = "Use this block to create documentation panels with title, description, and optional image."


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
        ("blockquote", blocks.BlockQuoteBlock()),
        ("raw_html", blocks.RawHTMLBlock()),
        ("code", CodeBlock(label="Code")),
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


# Helper: StreamField definitions shared by landing / index pages
def _body_blocks() -> list:
    return _inner_blocks() + [
        ("columns", RowBlock()),
    ]


def _topic_blocks() -> list:
    return [("topic_panel", DocumentationPanel())]
