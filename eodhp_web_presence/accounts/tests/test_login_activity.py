from datetime import UTC, date, datetime

import pytest
from django.test import SimpleTestCase

from ..keycloak_admin import HubEvent, HubUser
from ..login_activity import (
    aggregate_per_user,
    build_login_rows,
    month_choices,
    month_window,
    previous_month,
)

START = datetime(2026, 9, 1, tzinfo=UTC)
END = datetime(2026, 10, 1, tzinfo=UTC)


def at(day, hour=12):
    return datetime(2026, 9, day, hour, tzinfo=UTC)


def hub_user(user_id, created=datetime(2026, 1, 1, tzinfo=UTC)):
    return HubUser(
        id=user_id,
        username=user_id,
        email=f"{user_id}@example.com",
        email_verified=True,
        first_name="First",
        last_name="Last",
        enabled=True,
        created=created,
    )


def hub_event(event_type, user_id, time, client_id="portal", identity_provider=None, **extra):
    fields = {
        "id": None,
        "type": event_type,
        "time": time,
        "user_id": user_id,
        "client_id": client_id,
        "identity_provider": identity_provider,
        "register_method": None,
        "username": None,
        **extra,
    }
    return HubEvent(**fields)


class MonthWindowTestCase(SimpleTestCase):
    def test_september(self):
        self.assertEqual(month_window("2026-09"), (START, END))

    def test_december_rolls_over(self):
        self.assertEqual(
            month_window("2026-12"),
            (datetime(2026, 12, 1, tzinfo=UTC), datetime(2027, 1, 1, tzinfo=UTC)),
        )

    def test_invalid(self):
        for bad in ("2026-13", "2026-00", "2026/09", "september", "2026-9", ""):
            with self.subTest(month=bad), pytest.raises(ValueError, match="Invalid month"):
                month_window(bad)


class MonthChoicesTestCase(SimpleTestCase):
    def test_current_month_first_then_twelve_previous(self):
        choices = month_choices(date(2026, 10, 16))

        self.assertEqual(len(choices), 13)
        self.assertEqual(choices[0], ("2026-10", "October 2026 (to date)"))
        self.assertEqual(choices[1], ("2026-09", "September 2026"))
        self.assertEqual(choices[-1], ("2025-10", "October 2025"))

    def test_january_reaches_back_into_previous_year(self):
        choices = month_choices(date(2026, 1, 5), count=3)

        self.assertEqual(
            choices,
            [("2026-01", "January 2026 (to date)"), ("2025-12", "December 2025"), ("2025-11", "November 2025")],
        )

    def test_previous_month(self):
        self.assertEqual(previous_month(date(2026, 10, 16)), "2026-09")
        self.assertEqual(previous_month(date(2026, 1, 5)), "2025-12")


class BuildLoginRowsTestCase(SimpleTestCase):
    def test_one_row_per_login_in_time_order(self):
        users = {"ann": hub_user("ann")}
        events = [
            hub_event("LOGIN", "ann", at(3), client_id="notebooks"),
            hub_event("REGISTER", "ann", at(1)),
            hub_event("LOGIN", "ann", at(2)),
        ]

        rows = build_login_rows(events, users, START, END)

        self.assertEqual([row["login_time_utc"] for row in rows], [at(2), at(3)])
        self.assertEqual([row["client_id"] for row in rows], ["portal", "notebooks"])

    def test_out_of_window_and_user_less_events_ignored(self):
        users = {"ann": hub_user("ann")}
        events = [
            hub_event("LOGIN", "ann", START.replace(month=8, day=31, hour=23)),
            hub_event("LOGIN", "ann", END),
            hub_event("LOGIN", None, at(2)),
            hub_event("LOGIN", "ann", START),
        ]

        rows = build_login_rows(events, users, START, END)

        self.assertEqual([row["login_time_utc"] for row in rows], [START])

    def test_existing_user_maps_current_details(self):
        users = {"ann": hub_user("ann")}

        [row] = build_login_rows([hub_event("LOGIN", "ann", at(2), identity_provider="github")], users, START, END)

        self.assertEqual(
            row,
            {
                "login_time_utc": at(2),
                "user_id": "ann",
                "username": "ann",
                "email": "ann@example.com",
                "first_name": "First",
                "last_name": "Last",
                "identity_provider": "github",
                "client_id": "portal",
                "new_user": False,
                "first_login_of_new_user": False,
                "registered_via": None,
                "account_created_utc": datetime(2026, 1, 1, tzinfo=UTC),
                "user_deleted": False,
            },
        )

    def test_new_user_from_created_in_window(self):
        users = {"ann": hub_user("ann", created=at(1))}
        events = [hub_event("LOGIN", "ann", at(2)), hub_event("LOGIN", "ann", at(3))]

        rows = build_login_rows(events, users, START, END)

        self.assertEqual([row["new_user"] for row in rows], [True, True])
        self.assertEqual([row["first_login_of_new_user"] for row in rows], [True, False])

    def test_new_user_from_register_after_user_deleted(self):
        events = [
            hub_event("REGISTER", "gone", at(1), register_method="form"),
            hub_event("LOGIN", "gone", at(2), username="gone-user"),
        ]

        [row] = build_login_rows(events, {}, START, END)

        self.assertTrue(row["new_user"])
        self.assertTrue(row["first_login_of_new_user"])
        self.assertTrue(row["user_deleted"])
        self.assertEqual(row["username"], "gone-user")
        self.assertIsNone(row["email"])
        self.assertIsNone(row["account_created_utc"])
        self.assertEqual(row["registered_via"], "form")

    def test_registered_via_prefers_identity_provider(self):
        events = [
            hub_event("REGISTER", "ann", at(1), identity_provider="github", register_method="form"),
            hub_event("LOGIN", "ann", at(2)),
        ]

        [row] = build_login_rows(events, {"ann": hub_user("ann", created=at(1))}, START, END)

        self.assertEqual(row["registered_via"], "github")

    def test_register_before_window_not_new(self):
        events = [hub_event("REGISTER", "ann", START.replace(month=8)), hub_event("LOGIN", "ann", at(2))]

        [row] = build_login_rows(events, {"ann": hub_user("ann")}, START, END)

        self.assertFalse(row["new_user"])
        self.assertIsNone(row["registered_via"])


class AggregatePerUserTestCase(SimpleTestCase):
    def test_collapses_to_one_row_per_user(self):
        users = {"ann": hub_user("ann", created=at(1)), "bob": hub_user("bob")}
        events = [
            hub_event("LOGIN", "ann", at(2), client_id="portal", identity_provider="github"),
            hub_event("LOGIN", "bob", at(3)),
            hub_event("LOGIN", "ann", at(4), client_id="notebooks"),
            hub_event("LOGIN", "ann", at(5), client_id="portal", identity_provider="github"),
        ]

        ann, bob = aggregate_per_user(build_login_rows(events, users, START, END))

        self.assertEqual(
            ann,
            {
                "user_id": "ann",
                "username": "ann",
                "email": "ann@example.com",
                "first_name": "First",
                "last_name": "Last",
                "new_user": True,
                "account_created_utc": at(1),
                "login_count": 3,
                "first_login_utc": at(2),
                "last_login_utc": at(5),
                "identity_providers": "github",
                "clients": "portal;notebooks",
                "user_deleted": False,
            },
        )
        self.assertEqual(bob["login_count"], 1)
        self.assertEqual(bob["first_login_utc"], bob["last_login_utc"])
        self.assertEqual(bob["identity_providers"], "")

    def test_no_rows(self):
        self.assertEqual(aggregate_per_user([]), [])
