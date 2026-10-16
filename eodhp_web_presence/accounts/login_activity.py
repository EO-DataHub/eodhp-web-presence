import re
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime

from .keycloak_admin import HubEvent, HubUser

LOGIN_COLUMNS = (
    "login_time_utc",
    "user_id",
    "username",
    "email",
    "first_name",
    "last_name",
    "identity_provider",
    "client_id",
    "new_user",
    "first_login_of_new_user",
    "registered_via",
    "account_created_utc",
    "user_deleted",
)
PER_USER_COLUMNS = (
    "user_id",
    "username",
    "email",
    "first_name",
    "last_name",
    "new_user",
    "account_created_utc",
    "login_count",
    "first_login_utc",
    "last_login_utc",
    "identity_providers",
    "clients",
    "user_deleted",
)

Row = dict[str, object]


def _month_start(year: int, month: int) -> datetime:
    return datetime(year + (month - 1) // 12, (month - 1) % 12 + 1, 1, tzinfo=UTC)


def month_window(month: str) -> tuple[datetime, datetime]:
    """'YYYY-MM' to a half-open UTC window covering that calendar month."""
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError(f"Invalid month {month!r}")
    year, number = (int(part) for part in month.split("-"))
    if not 1 <= number <= 12:
        raise ValueError(f"Invalid month {month!r}")
    return _month_start(year, number), _month_start(year, number + 1)


def previous_month(today: date) -> str:
    return _month_start(today.year, today.month - 1).strftime("%Y-%m")


def month_choices(today: date, count: int = 13) -> list[tuple[str, str]]:
    choices = []
    for offset in range(count):
        start = _month_start(today.year, today.month - offset)
        label = start.strftime("%B %Y")
        choices.append((start.strftime("%Y-%m"), f"{label} (to date)" if offset == 0 else label))
    return choices


def build_login_rows(
    events: Iterable[HubEvent], users_by_id: Mapping[str, HubUser], start: datetime, end: datetime
) -> list[Row]:
    """One row per LOGIN in the window; REGISTER events only mark users as new and say how they signed up."""
    in_window = sorted(
        (event for event in events if event.user_id and start <= event.time < end),
        key=lambda event: event.time,
    )
    registered_via = {
        event.user_id: event.identity_provider or event.register_method
        for event in in_window
        if event.type == "REGISTER"
    }
    # A REGISTER also counts, so users deleted since signing up are still new
    new_users = {user.id for user in users_by_id.values() if user.created and start <= user.created < end}
    new_users |= registered_via.keys()

    rows: list[Row] = []
    seen_new: set[str] = set()
    for event in in_window:
        if event.type != "LOGIN":
            continue
        user_id = event.user_id
        user = users_by_id.get(user_id)
        new_user = user_id in new_users
        rows.append(
            {
                "login_time_utc": event.time,
                "user_id": user_id,
                "username": user.username if user else event.username,
                "email": user.email if user else None,
                "first_name": user.first_name if user else None,
                "last_name": user.last_name if user else None,
                "identity_provider": event.identity_provider,
                "client_id": event.client_id,
                "new_user": new_user,
                "first_login_of_new_user": new_user and user_id not in seen_new,
                "registered_via": registered_via.get(user_id),
                "account_created_utc": user.created if user else None,
                "user_deleted": user is None,
            }
        )
        if new_user:
            seen_new.add(user_id)
    return rows


def aggregate_per_user(rows: Iterable[Row]) -> list[Row]:
    """Collapse login rows, in time order, to one row per user."""
    logins: dict[object, list[Row]] = {}
    for row in rows:
        logins.setdefault(row["user_id"], []).append(row)
    summaries = []
    for user_logins in logins.values():
        first, last = user_logins[0], user_logins[-1]
        providers = dict.fromkeys(str(row["identity_provider"]) for row in user_logins if row["identity_provider"])
        clients = dict.fromkeys(str(row["client_id"]) for row in user_logins if row["client_id"])
        summaries.append(
            {
                **{column: first.get(column) for column in PER_USER_COLUMNS},
                "login_count": len(user_logins),
                "first_login_utc": first["login_time_utc"],
                "last_login_utc": last["login_time_utc"],
                "identity_providers": ";".join(providers),
                "clients": ";".join(clients),
            }
        )
    return summaries
