from datetime import UTC, datetime
from http import HTTPStatus
from unittest import mock

import jwt
from django.conf import settings
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from ..keycloak_admin import HubUser, KeycloakAdminUnavailable
from ..models import User
from ..wagtail_hooks import HubUsersMenuItem

KEYCLOAK_ENABLED = {
    "USER_LIST_ENABLED": True,
    "ADMIN_BASE_URL": "https://keycloak.example/keycloak",
    "REALM": "test",
    "ADMIN_CLIENT_ID": "web-presence-admin",
    "ADMIN_CLIENT_SECRET": "s3cret",
    "ADMIN_TIMEOUT": 5.0,
    "ADMIN_PAGE_SIZE": 200,
}
KEYCLOAK_DISABLED = {**KEYCLOAK_ENABLED, "USER_LIST_ENABLED": False, "ADMIN_CLIENT_SECRET": None}
OIDC_CLAIMS_ENABLED = {
    "ENABLED": True,
    "USERNAME_PATH": "username",
    "EMAIL_PATH": "email",
    "ROLES_PATH": "roles",
    "SUPERUSER_ROLE": "admin",
    "MODERATOR_ROLE": "moderator",
    "EDITOR_ROLE": "editor",
}
OIDC_CLAIMS_DISABLED = {**OIDC_CLAIMS_ENABLED, "ENABLED": False}

USERS = [
    HubUser(
        id="id-1",
        username="=cmd",
        email="cmd@example.com",
        email_verified=True,
        first_name="+Plus",
        last_name=None,
        enabled=True,
        created=datetime(2024, 1, 2, 3, 4, 5, tzinfo=UTC),
    ),
    HubUser(
        id="id-2",
        username="zoe",
        email=None,
        email_verified=False,
        first_name="Zoe",
        last_name="Smith",
        enabled=False,
        created=None,
    ),
]


def claims_middleware():
    middleware = list(settings.MIDDLEWARE)
    factory = "eodhp_web_presence.settings.claims_middleware_factory"
    if factory not in middleware:
        middleware.insert(
            middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
            factory,
        )
    return middleware


def bearer(username, roles=()):
    return "Bearer " + jwt.encode(
        {"username": username, "email": f"{username}@example.com", "roles": list(roles)},
        "secret",
        algorithm="HS256",
    )


def fake_client(users=USERS):
    client = mock.Mock()
    client.count_users.return_value = len(users)
    client.list_users.return_value = list(users)
    client.iter_users.return_value = iter(users)
    return client


class HubUsersViewsTestCase(TestCase):
    def setUp(self):
        self.index_url = reverse("hub_users_index")
        self.export_url = reverse("hub_users_export")
        self.superuser = User.objects.create_superuser(username="admin", password="pw")
        self.client_patch = mock.patch("accounts.views.get_client", return_value=fake_client())
        self.get_client = self.client_patch.start()
        self.addCleanup(self.client_patch.stop)

    @override_settings(KEYCLOAK=KEYCLOAK_DISABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_disabled__404_and_menu_hidden(self):
        self.client.force_login(self.superuser)

        self.assertEqual(self.client.get(self.index_url).status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.client.get(self.export_url).status_code, HTTPStatus.NOT_FOUND)

        request = RequestFactory().get(self.index_url)
        request.user = self.superuser
        self.assertFalse(HubUsersMenuItem("Hub users", self.index_url).is_shown(request))

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_anonymous__redirected_to_login(self):
        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("wagtailadmin_login"), response["Location"])

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_non_superuser__denied(self):
        user = User.objects.create_user(username="editor", password="pw")
        self.client.force_login(user)

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotContains(self.client.get(self.index_url, follow=True), "Download CSV")
        request = RequestFactory().get(self.index_url)
        request.user = user
        self.assertFalse(HubUsersMenuItem("Hub users", self.index_url).is_shown(request))

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_superuser_without_oidc__lists_users(self):
        self.client.force_login(self.superuser)

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "=cmd")
        self.assertContains(response, "zoe")
        self.assertContains(response, "Download CSV")
        self.assertContains(response, "2 users")
        request = RequestFactory().get(self.index_url)
        request.user = self.superuser
        self.assertTrue(HubUsersMenuItem("Hub users", self.index_url).is_shown(request))

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_ENABLED, MIDDLEWARE=claims_middleware())
    def test_superuser_with_claims_not_admin__denied(self):
        self.client.force_login(self.superuser)

        with self.assertLogs("accounts.audit", level="WARNING") as logs:
            response = self.client.get(self.index_url, headers={"Authorization": bearer("admin", roles=["editor"])})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], reverse("wagtailadmin_home"))
        self.assertIn("hub-users access denied user=admin", logs.output[0])
        self.get_client.return_value.count_users.assert_not_called()

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_ENABLED, MIDDLEWARE=claims_middleware())
    def test_superuser_with_claims_admin__lists_users_and_forwards_search(self):
        headers = {"Authorization": bearer("admin", roles=["admin"])}

        response = self.client.get(self.index_url, {"q": "zo"}, headers=headers)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "zoe")
        client = self.get_client.return_value
        client.count_users.assert_called_once_with(search="zo")
        client.list_users.assert_called_once_with(search="zo", first=0, max=50)
        self.assertContains(response, f'href="{self.export_url}?q=zo"')

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_index__second_page_offsets_keycloak_query(self):
        self.client.force_login(self.superuser)
        self.get_client.return_value.count_users.return_value = 120

        response = self.client.get(self.index_url, {"p": "3"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.get_client.return_value.list_users.assert_called_once_with(search=None, first=100, max=50)
        self.assertContains(response, "Page 3 of 3")

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_index__keycloak_error__message_not_500(self):
        self.client.force_login(self.superuser)
        self.get_client.return_value.count_users.side_effect = KeycloakAdminUnavailable("down")

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, "Could not reach the identity service")
        self.assertNotContains(response, "zoe")

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__csv_with_headers_guard_and_audit(self):
        self.client.force_login(self.superuser)

        with self.assertLogs("accounts.audit", level="INFO") as logs:
            response = self.client.get(self.export_url, {"q": "x"})
            body = b"".join(response.streaming_content).decode()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertRegex(response["Content-Disposition"], r'^attachment; filename="eodh-hub-users-\d{8}T\d{6}Z\.csv"$')
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(
            body.splitlines(),
            [
                "id,username,email,email_verified,first_name,last_name,enabled,created",
                "id-1,'=cmd,cmd@example.com,true,'+Plus,,true,2024-01-02T03:04:05Z",
                "id-2,zoe,,false,Zoe,Smith,false,",
            ],
        )
        self.get_client.return_value.iter_users.assert_called_once_with(search="x")
        self.assertIn("hub-users export by user=admin search='x' rows=2", logs.output[0])

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__keycloak_error__502_not_truncated_csv(self):
        self.client.force_login(self.superuser)
        self.get_client.return_value.iter_users.side_effect = KeycloakAdminUnavailable("down")

        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, HTTPStatus.BAD_GATEWAY)
        self.assertNotIn("Content-Disposition", response)

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__anonymous_redirected(self):
        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("wagtailadmin_login"), response["Location"])
