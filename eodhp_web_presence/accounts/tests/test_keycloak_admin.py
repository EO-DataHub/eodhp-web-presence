from datetime import UTC, datetime
from unittest import mock

import pytest
import urllib3
from django.test import SimpleTestCase
from django.test.utils import override_settings

from ..keycloak_admin import (
    HubEvent,
    HubUser,
    KeycloakAdminAuthError,
    KeycloakAdminClient,
    KeycloakAdminError,
    KeycloakAdminUnavailable,
    get_client,
)

BASE_URL = "https://keycloak.example/keycloak"
TOKEN_URL = f"{BASE_URL}/realms/test/protocol/openid-connect/token"
USERS_URL = f"{BASE_URL}/admin/realms/test/users"
EVENTS_URL = f"{BASE_URL}/admin/realms/test/events"
SEPTEMBER = (datetime(2026, 9, 1, tzinfo=UTC), datetime(2026, 10, 1, tzinfo=UTC))


def response(status=200, data=None):
    return mock.Mock(status=status, json=mock.Mock(return_value=data))


def token_response(token="token-1", expires_in=300):
    return response(200, {"access_token": token, "expires_in": expires_in})


def user_json(username, **extra):
    return {"id": f"id-{username}", "username": username, "enabled": True, **extra}


SEPTEMBER_MS = 1788220800000


def event_json(event_id, time=SEPTEMBER_MS, **extra):
    return {"id": event_id, "type": "LOGIN", "time": time, "userId": "id-ann", **extra}


def make_client(http, page_size=2):
    return KeycloakAdminClient(
        base_url=BASE_URL + "/",
        realm="test",
        client_id="web-presence-admin",
        client_secret="s3cret",
        page_size=page_size,
        http=http,
    )


class KeycloakAdminClientTestCase(SimpleTestCase):
    def setUp(self):
        self.http = mock.Mock()
        self.client = make_client(self.http)

    def calls(self, method=None):
        return [call for call in self.http.request.call_args_list if method is None or call.args[0] == method]

    def test_token__requested_once_and_reused(self):
        self.http.request.side_effect = [token_response(), response(200, 3), response(200, 4)]

        self.assertEqual(self.client.count_users(), 3)
        self.assertEqual(self.client.count_users(), 4)

        token_calls = self.calls("POST")
        self.assertEqual(len(token_calls), 1)
        self.assertEqual(token_calls[0].args[1], TOKEN_URL)
        self.assertEqual(token_calls[0].kwargs["body"], "grant_type=client_credentials")
        self.assertTrue(token_calls[0].kwargs["headers"]["Authorization"].startswith("Basic "))
        for call in self.calls("GET"):
            self.assertEqual(call.kwargs["headers"]["Authorization"], "Bearer token-1")

    def test_token__refreshed_after_expiry(self):
        self.http.request.side_effect = [
            token_response("token-1", expires_in=100),
            response(200, 1),
            token_response("token-2"),
            response(200, 1),
        ]
        with mock.patch("accounts.keycloak_admin.time.monotonic", side_effect=[0.0, 200.0, 200.0]):
            self.client.count_users()
            self.client.count_users()

        self.assertEqual(len(self.calls("POST")), 2)
        self.assertEqual(self.calls("GET")[1].kwargs["headers"]["Authorization"], "Bearer token-2")

    def test_users_401__refreshes_token_once_then_retries(self):
        self.http.request.side_effect = [
            token_response("token-1"),
            response(401),
            token_response("token-2"),
            response(200, 7),
        ]

        self.assertEqual(self.client.count_users(), 7)
        self.assertEqual(self.calls("GET")[1].kwargs["headers"]["Authorization"], "Bearer token-2")

    def test_users_401_twice__raises_auth_error(self):
        self.http.request.side_effect = [token_response(), response(401), token_response(), response(401)]

        with pytest.raises(KeycloakAdminAuthError):
            self.client.count_users()

    def test_users_403__raises_auth_error(self):
        self.http.request.side_effect = [token_response(), response(403)]

        with pytest.raises(KeycloakAdminAuthError):
            self.client.list_users()

    def test_users_500__raises_unavailable(self):
        self.http.request.side_effect = [token_response(), response(503)]

        with pytest.raises(KeycloakAdminUnavailable):
            self.client.list_users()

    def test_users_other_status__raises_error(self):
        self.http.request.side_effect = [token_response(), response(400)]

        with pytest.raises(KeycloakAdminError):
            self.client.list_users()

    def test_network_error__raises_unavailable(self):
        self.http.request.side_effect = [token_response(), urllib3.exceptions.MaxRetryError(None, USERS_URL)]

        with pytest.raises(KeycloakAdminUnavailable):
            self.client.list_users()

    def test_token_network_error__raises_unavailable(self):
        self.http.request.side_effect = urllib3.exceptions.ConnectTimeoutError()

        with pytest.raises(KeycloakAdminUnavailable):
            self.client.count_users()

    def test_token_401__raises_auth_error(self):
        self.http.request.side_effect = [response(401, {"error": "unauthorized_client"})]

        with pytest.raises(KeycloakAdminAuthError):
            self.client.count_users()
        self.assertEqual(len(self.calls("GET")), 0)

    def test_list_users__requests_attributes_and_sends_search(self):
        self.http.request.side_effect = [token_response(), response(200, [])]

        self.client.list_users(search="bob", first=10, max=5)

        call = self.calls("GET")[0]
        self.assertEqual(call.args[1], USERS_URL)
        self.assertEqual(
            call.kwargs["fields"],
            {"briefRepresentation": "false", "first": "10", "max": "5", "search": "bob"},
        )

    def test_count_users__forwards_search_only_when_set(self):
        self.http.request.side_effect = [token_response(), response(200, 1), response(200, 2)]

        self.client.count_users()
        self.client.count_users(search="ann")

        first, second = self.calls("GET")
        self.assertEqual(first.args[1], f"{USERS_URL}/count")
        self.assertEqual(first.kwargs["fields"], {})
        self.assertEqual(second.kwargs["fields"], {"search": "ann"})

    def test_list_users__sorted_by_username(self):
        self.http.request.side_effect = [token_response(), response(200, [user_json("zoe"), user_json("adam")])]

        users = self.client.list_users()

        self.assertEqual([user.username for user in users], ["adam", "zoe"])

    def test_iter_users__pages_until_short_page(self):
        self.http.request.side_effect = [
            token_response(),
            response(200, [user_json("a"), user_json("b")]),
            response(200, [user_json("c"), user_json("d")]),
            response(200, [user_json("e")]),
        ]

        users = list(self.client.iter_users(search="x"))

        self.assertEqual([user.username for user in users], ["a", "b", "c", "d", "e"])
        firsts = [call.kwargs["fields"]["first"] for call in self.calls("GET")]
        self.assertEqual(firsts, ["0", "2", "4"])
        for call in self.calls("GET"):
            self.assertEqual(call.kwargs["fields"]["max"], "2")
            self.assertEqual(call.kwargs["fields"]["search"], "x")

    def test_iter_users__empty_realm(self):
        self.http.request.side_effect = [token_response(), response(200, [])]

        self.assertEqual(list(self.client.iter_users()), [])
        self.assertEqual(len(self.calls("GET")), 1)

    def test_iter_events__sends_window_and_repeated_types(self):
        self.http.request.side_effect = [token_response(), response(200, [])]

        list(self.client.iter_events(start=SEPTEMBER[0], end=SEPTEMBER[1]))

        call = self.calls("GET")[0]
        self.assertEqual(call.args[1], EVENTS_URL)
        self.assertEqual(
            call.kwargs["fields"],
            [
                ("type", "LOGIN"),
                ("type", "REGISTER"),
                ("dateFrom", "1788220800000"),
                ("dateTo", "1790812799999"),
                ("direction", "asc"),
                ("first", "0"),
                ("max", "2"),
            ],
        )

    def test_iter_events__pages_from_last_event_time(self):
        self.http.request.side_effect = [
            token_response(),
            response(200, [event_json("e1", SEPTEMBER_MS + 1), event_json("e2", SEPTEMBER_MS + 5)]),
            response(200, [event_json("e2", SEPTEMBER_MS + 5), event_json("e3", SEPTEMBER_MS + 9)]),
            response(200, [event_json("e3", SEPTEMBER_MS + 9)]),
        ]

        events = list(self.client.iter_events(start=SEPTEMBER[0], end=SEPTEMBER[1]))

        self.assertEqual([event.id for event in events], ["e1", "e2", "e3"])
        for call, date_from in zip(self.calls("GET"), (SEPTEMBER_MS, SEPTEMBER_MS + 5, SEPTEMBER_MS + 9), strict=True):
            self.assertEqual(
                call.kwargs["fields"],
                [
                    ("type", "LOGIN"),
                    ("type", "REGISTER"),
                    ("dateFrom", str(date_from)),
                    ("dateTo", "1790812799999"),
                    ("direction", "asc"),
                    ("first", "0"),
                    ("max", "2"),
                ],
            )

    def test_iter_events__ties_across_page_boundary_not_skipped(self):
        # e2 and e3 share a millisecond and Keycloak may order them either way; offset paging could
        # return e2 on both pages and never return e3
        tie = SEPTEMBER_MS + 5
        self.http.request.side_effect = [
            token_response(),
            response(200, [event_json("e1", SEPTEMBER_MS + 1), event_json("e2", tie)]),
            response(200, [event_json("e3", tie), event_json("e4", tie + 1)]),
            response(200, [event_json("e4", tie + 1)]),
        ]

        events = list(self.client.iter_events(start=SEPTEMBER[0], end=SEPTEMBER[1]))

        self.assertEqual([event.id for event in events], ["e1", "e2", "e3", "e4"])
        date_froms = [dict(call.kwargs["fields"])["dateFrom"] for call in self.calls("GET")]
        self.assertEqual(date_froms, [str(SEPTEMBER_MS), str(tie), str(tie + 1)])

    def test_iter_events__full_page_in_one_millisecond__raises(self):
        self.http.request.side_effect = [
            token_response(),
            response(200, [event_json("e1", SEPTEMBER_MS + 5), event_json("e2", SEPTEMBER_MS + 5)]),
            response(200, [event_json("e1", SEPTEMBER_MS + 5), event_json("e2", SEPTEMBER_MS + 5)]),
        ]

        with pytest.raises(KeycloakAdminError, match="At least 2 events"):
            list(self.client.iter_events(start=SEPTEMBER[0], end=SEPTEMBER[1]))
        self.assertEqual(len(self.calls("GET")), 2)

    def test_iter_events__id_less_events_kept_once(self):
        self.http.request.side_effect = [
            token_response(),
            response(200, [event_json(None, SEPTEMBER_MS + 1), event_json(None, SEPTEMBER_MS + 5)]),
            response(200, [event_json(None, SEPTEMBER_MS + 5), event_json(None, SEPTEMBER_MS + 9, userId="id-bob")]),
            response(200, [event_json(None, SEPTEMBER_MS + 9, userId="id-bob")]),
        ]

        events = list(self.client.iter_events(start=SEPTEMBER[0], end=SEPTEMBER[1]))

        self.assertEqual([event.user_id for event in events], ["id-ann", "id-ann", "id-bob"])

    def test_iter_events__empty(self):
        self.http.request.side_effect = [token_response(), response(200, [])]

        self.assertEqual(list(self.client.iter_events(start=SEPTEMBER[0], end=SEPTEMBER[1])), [])
        self.assertEqual(len(self.calls("GET")), 1)

    def test_iter_events_403__raises_auth_error(self):
        self.http.request.side_effect = [token_response(), response(403)]

        with pytest.raises(KeycloakAdminAuthError):
            list(self.client.iter_events(start=SEPTEMBER[0], end=SEPTEMBER[1]))


class HubEventTestCase(SimpleTestCase):
    def test_from_json__maps_fields(self):
        event = HubEvent.from_json(
            {
                "id": "e1",
                "type": "REGISTER",
                "time": 1788251400000,
                "userId": "id-ann",
                "clientId": "portal",
                "ipAddress": "192.0.2.1",
                "sessionId": "s1",
                "details": {
                    "identity_provider": "github",
                    "register_method": "form",
                    "username": "ann",
                    "redirect_uri": "https://example.com",
                },
            }
        )

        self.assertEqual(
            event,
            HubEvent(
                id="e1",
                type="REGISTER",
                time=datetime(2026, 9, 1, 8, 30, tzinfo=UTC),
                user_id="id-ann",
                client_id="portal",
                identity_provider="github",
                register_method="form",
                username="ann",
            ),
        )

    def test_from_json__missing_details_are_none(self):
        event = HubEvent.from_json({"type": "LOGIN", "time": 1788220800000})

        self.assertIsNone(event.id)
        self.assertIsNone(event.user_id)
        self.assertIsNone(event.client_id)
        self.assertIsNone(event.identity_provider)
        self.assertIsNone(event.register_method)
        self.assertIsNone(event.username)


class HubUserTestCase(SimpleTestCase):
    def test_from_json__maps_fields(self):
        user = HubUser.from_json(
            {
                "id": "abc",
                "username": "ann",
                "email": "ann@example.com",
                "emailVerified": True,
                "firstName": "Ann",
                "lastName": "Example",
                "enabled": True,
                "createdTimestamp": 1700000000000,
                "attributes": {"secret": ["ignored"], "lastLoginTime": ["1788251400000"]},
            }
        )

        self.assertEqual(
            user,
            HubUser(
                id="abc",
                username="ann",
                email="ann@example.com",
                email_verified=True,
                first_name="Ann",
                last_name="Example",
                enabled=True,
                created=datetime(2023, 11, 14, 22, 13, 20, tzinfo=UTC),
                last_login=datetime(2026, 9, 1, 8, 30, tzinfo=UTC),
            ),
        )

    def test_from_json__missing_optionals_are_none(self):
        user = HubUser.from_json({"id": "abc", "username": "ann"})

        self.assertIsNone(user.email)
        self.assertIsNone(user.first_name)
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.created)
        self.assertIsNone(user.last_login)
        self.assertFalse(user.email_verified)
        self.assertFalse(user.enabled)

    def test_from_json__last_login_ignores_non_numeric_values(self):
        user = HubUser.from_json({"id": "abc", "username": "ann", "attributes": {"lastLoginTime": ["", "soon", "-1"]}})

        self.assertIsNone(user.last_login)

    def test_from_json__last_login_takes_largest_value(self):
        user = HubUser.from_json(
            {
                "id": "abc",
                "username": "ann",
                "attributes": {"lastLoginTime": ["1788251400000", "bad", "1788220800000"]},
            }
        )

        self.assertEqual(user.last_login, datetime(2026, 9, 1, 8, 30, tzinfo=UTC))

    def test_from_json__last_login_ignores_out_of_range_values(self):
        user = HubUser.from_json(
            {
                "id": "abc",
                "username": "ann",
                "attributes": {"lastLoginTime": ["9223372036854775807", "1788251400000"]},
            }
        )

        self.assertEqual(user.last_login, datetime(2026, 9, 1, 8, 30, tzinfo=UTC))


class GetClientTestCase(SimpleTestCase):
    @override_settings(KEYCLOAK={"USER_LIST_ENABLED": False, "ADMIN_CLIENT_SECRET": None})
    def test_disabled__returns_none(self):
        self.assertIsNone(get_client())

    @override_settings(
        KEYCLOAK={
            "USER_LIST_ENABLED": True,
            "ADMIN_BASE_URL": BASE_URL,
            "REALM": "test",
            "ADMIN_CLIENT_ID": "web-presence-admin",
            "ADMIN_CLIENT_SECRET": "s3cret",
            "ADMIN_TIMEOUT": 5.0,
            "ADMIN_PAGE_SIZE": 50,
        }
    )
    def test_enabled__builds_client_from_settings(self):
        client = get_client()

        self.assertIsInstance(client, KeycloakAdminClient)
        self.assertEqual(client.users_url, USERS_URL)
        self.assertEqual(client.events_url, EVENTS_URL)
        self.assertEqual(client.page_size, 50)
