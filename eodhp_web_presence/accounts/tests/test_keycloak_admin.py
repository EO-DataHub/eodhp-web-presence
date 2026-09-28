from datetime import UTC, datetime
from unittest import mock

import pytest
import urllib3
from django.test import SimpleTestCase
from django.test.utils import override_settings

from ..keycloak_admin import (
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


def response(status=200, data=None):
    return mock.Mock(status=status, json=mock.Mock(return_value=data))


def token_response(token="token-1", expires_in=300):
    return response(200, {"access_token": token, "expires_in": expires_in})


def user_json(username, **extra):
    return {"id": f"id-{username}", "username": username, "enabled": True, **extra}


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

    def test_list_users__sends_brief_representation_and_search(self):
        self.http.request.side_effect = [token_response(), response(200, [])]

        self.client.list_users(search="bob", first=10, max=5)

        call = self.calls("GET")[0]
        self.assertEqual(call.args[1], USERS_URL)
        self.assertEqual(
            call.kwargs["fields"],
            {"briefRepresentation": "true", "first": "10", "max": "5", "search": "bob"},
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
                "attributes": {"secret": ["ignored"]},
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
            ),
        )

    def test_from_json__missing_optionals_are_none(self):
        user = HubUser.from_json({"id": "abc", "username": "ann"})

        self.assertIsNone(user.email)
        self.assertIsNone(user.first_name)
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.created)
        self.assertFalse(user.email_verified)
        self.assertFalse(user.enabled)


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
        self.assertEqual(client.page_size, 50)
