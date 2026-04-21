from collections.abc import Generator
from unittest.mock import patch

import pytest
from home import icons

_TEST_ICONS = {
    "account": (
        "M12,4A4,4 0 0,1 16,8A4,4 0 0,1 12,12A4,4 0 0,1 8,8A4,4 0 0,1 12,4"
        "M12,14C16.42,14 20,15.79 20,18V20H4V18C4,15.79 7.58,14 12,14Z"
    ),
}


@pytest.fixture(scope="session", autouse=True)
def _stub_mdi_icons() -> Generator[None]:
    icons._load_icon_map.cache_clear()
    with patch.object(icons, "_icon_map", return_value=_TEST_ICONS):
        yield
