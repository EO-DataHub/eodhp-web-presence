"""Tests for the BlockQuoteToStructOperation in migration 0014."""

import copy
import importlib

from django.apps import apps

_migration_module = (
    f"{apps.get_app_config('home').name}.migrations.0014_alter_aboutindexpage_body_alter_casestudiespage_body_and_more"
)
_m0014 = importlib.import_module(_migration_module)
_QUOTE_DEFAULTS = _m0014._QUOTE_DEFAULTS
_op = _m0014.BlockQuoteToStructOperation()


# -- apply: converts string blockquotes to struct -----------------------------


def test_apply_converts_string_to_struct():
    stream = [{"type": "blockquote", "value": "Hello world"}]
    result = _op.apply(stream)
    assert result[0]["value"] == {"quote": "Hello world", **_QUOTE_DEFAULTS}


def test_apply_ignores_non_blockquote():
    stream = [{"type": "content_block", "value": "some text"}]
    original = copy.deepcopy(stream)
    result = _op.apply(stream)
    assert result == original


def test_apply_ignores_already_converted():
    stream = [{"type": "blockquote", "value": {"quote": "Already done", **_QUOTE_DEFAULTS}}]
    original = copy.deepcopy(stream)
    result = _op.apply(stream)
    assert result == original


def test_apply_mixed_stream():
    stream = [
        {"type": "blockquote", "value": "Convert me"},
        {"type": "content_block", "value": "leave me alone"},
    ]
    result = _op.apply(stream)
    assert result[0]["value"] == {"quote": "Convert me", **_QUOTE_DEFAULTS}
    assert result[1]["value"] == "leave me alone"


def test_apply_preserves_block_id():
    stream = [{"type": "blockquote", "value": "Hello", "id": "abc123"}]
    result = _op.apply(stream)
    assert result[0]["id"] == "abc123"
    assert result[0]["type"] == "blockquote"
