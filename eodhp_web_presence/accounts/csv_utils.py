from datetime import UTC, datetime

FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def csv_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = str(value)
    # Stop spreadsheets from evaluating user-supplied cells as formulas
    if text.startswith(FORMULA_PREFIXES):
        return "'" + text
    return text
