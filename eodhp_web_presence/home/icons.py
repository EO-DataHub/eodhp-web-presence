"""Server-side MDI icon path lookup.

Path data is baked into `mdi_icons.json` at build time (see
`scripts/build_mdi_icons.mjs`). The file is lazy-loaded on first access;
each icon lookup is a dict hit.
"""

import json
from functools import lru_cache
from pathlib import Path

_DATA_FILE = Path(__file__).resolve().parent.parent / "dist" / "mdi_icons.json"


@lru_cache
def _load_icon_map() -> dict[str, str]:
    with _DATA_FILE.open() as f:
        payload = json.load(f)
    return payload.get("icons", {})


def _icon_map() -> dict[str, str]:
    if not _DATA_FILE.exists():
        return {}
    return _load_icon_map()


def get_icon_path(name: str) -> str | None:
    """Return the raw SVG `d` attribute for `name`, or None if unknown."""
    return _icon_map().get(name)
