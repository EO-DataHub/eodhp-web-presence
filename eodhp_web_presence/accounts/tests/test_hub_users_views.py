from datetime import UTC, datetime
from http import HTTPStatus
from unittest import mock

from django.conf import settings
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.urls import reverse
from wagtail.users.models import UserProfile

from ..keycloak_admin import HubEvent, HubUser, KeycloakAdminAuthError, KeycloakAdminUnavailable
from ..models import User
from ..wagtail_hooks import HubUsersMenuItem
from .jwt_helpers import mock_jwks, sign_token

KEYCLOAK_ENABLED = {
    "CLIENT_ID": "eodh",
    "CERTS_URL": "https://keycloak.example/keycloak/realms/test/protocol/openid-connect/certs",
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

EVENTS = [
    HubEvent(
        id="e1",
        type="REGISTER",
        time=datetime(2026, 9, 2, 10, 0, tzinfo=UTC),
        user_id="id-gone",
        client_id="portal",
        identity_provider=None,
        register_method="form",
        username="-gone",
    ),
    HubEvent(
        id="e2",
        type="LOGIN",
        time=datetime(2026, 9, 2, 10, 1, tzinfo=UTC),
        user_id="id-gone",
        client_id="portal",
        identity_provider=None,
        register_method=None,
        username="-gone",
    ),
    HubEvent(
        id="e3",
        type="LOGIN",
        time=datetime(2026, 9, 3, 8, 0, tzinfo=UTC),
        user_id="id-1",
        client_id="portal",
        identity_provider="github",
        register_method=None,
        username="=cmd",
    ),
    HubEvent(
        id="e4",
        type="LOGIN",
        time=datetime(2026, 9, 4, 8, 0, tzinfo=UTC),
        user_id="id-1",
        client_id="notebooks",
        identity_provider=None,
        register_method=None,
        username="=cmd",
    ),
]
NOW = datetime(2026, 10, 16, 9, 0, tzinfo=UTC)


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
    # Signed with the throwaway test key; tests run inside mock_jwks() so it verifies.
    return "Bearer " + sign_token(username=username, email=f"{username}@example.com", roles=list(roles))


def fake_client(users=USERS, events=EVENTS):
    client = mock.Mock()
    client.count_users.return_value = len(users)
    client.list_users.return_value = list(users)
    client.iter_users.return_value = iter(users)
    client.iter_events.return_value = iter(events)
    return client


class HubUsersViewsTestCase(TestCase):
    def setUp(self):
        self.index_url = reverse("hub_users_index")
        self.export_url = reverse("hub_users_export")
        self.superuser = User.objects.create_superuser(username="admin", password="pw")
        self.client_patch = mock.patch("accounts.views.get_client", return_value=fake_client())
        self.get_client = self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
        jwks = mock_jwks()
        jwks.__enter__()
        self.addCleanup(jwks.__exit__, None, None, None)

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
            body = response.content.decode()

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
    def test_export__keycloak_error_after_first_page__502_not_partial_csv(self):
        self.client.force_login(self.superuser)

        def users_then_error():
            yield USERS[0]
            raise KeycloakAdminUnavailable("down")

        self.get_client.return_value.iter_users.return_value = users_then_error()

        with self.assertNoLogs("accounts.audit", level="INFO"):
            response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, HTTPStatus.BAD_GATEWAY)
        self.assertNotIn("=cmd", response.content.decode())
        self.assertNotIn("Content-Disposition", response)

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_index__created_shown_in_utc_regardless_of_profile_timezone(self):
        profile = UserProfile.get_for_user(self.superuser)
        profile.current_time_zone = "Pacific/Auckland"
        profile.save()
        self.client.force_login(self.superuser)

        response = self.client.get(self.index_url)

        self.assertContains(response, "2024-01-02 03:04 UTC")
        self.assertNotContains(response, "2024-01-02 16:04")

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_index__search_form_submits_with_visible_button(self):
        self.client.force_login(self.superuser)

        response = self.client.get(self.index_url, {"q": "zo"})

        self.assertContains(response, f'<form method="get" action="{self.index_url}" role="search"')
        self.assertContains(response, '<button type="submit" class="button">Search</button>')
        self.assertNotContains(response, "<input disabled")
        self.assertContains(response, 'value="zo"')

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_index__links_to_login_activity(self):
        self.client.force_login(self.superuser)

        response = self.client.get(self.index_url)

        self.assertContains(response, f'href="{reverse("hub_users_login_activity")}"')

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__anonymous_redirected(self):
        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(reverse("wagtailadmin_login"), response["Location"])


class LoginActivityViewsTestCase(TestCase):
    def setUp(self):
        self.page_url = reverse("hub_users_login_activity")
        self.export_url = reverse("hub_users_login_activity_export")
        self.superuser = User.objects.create_superuser(username="admin", password="pw")
        self.client_patch = mock.patch("accounts.views.get_client", return_value=fake_client())
        self.get_client = self.client_patch.start()
        self.addCleanup(self.client_patch.stop)
        # Pin "today" so the month choices, and the September export, don't drift with the calendar
        datetime_patch = mock.patch("accounts.views.datetime", wraps=datetime)
        datetime_patch.start().now.return_value = NOW
        self.addCleanup(datetime_patch.stop)
        jwks = mock_jwks()
        jwks.__enter__()
        self.addCleanup(jwks.__exit__, None, None, None)

    def assert_keycloak_not_called(self):
        client = self.get_client.return_value
        client.iter_events.assert_not_called()
        client.iter_users.assert_not_called()
        client.count_users.assert_not_called()

    @override_settings(KEYCLOAK=KEYCLOAK_DISABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_disabled__404(self):
        self.client.force_login(self.superuser)

        self.assertEqual(self.client.get(self.page_url).status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(
            self.client.get(self.export_url, {"month": "2026-09", "kind": "logins"}).status_code,
            HTTPStatus.NOT_FOUND,
        )

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_anonymous__redirected_to_login(self):
        for url in (self.page_url, self.export_url):
            with self.subTest(url=url):
                response = self.client.get(url, {"month": "2026-09", "kind": "logins"})

                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertIn(reverse("wagtailadmin_login"), response["Location"])

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_non_superuser__denied(self):
        self.client.force_login(User.objects.create_user(username="editor", password="pw"))

        response = self.client.get(self.export_url, {"month": "2026-09", "kind": "logins"})

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotIn("Content-Disposition", response)
        self.assert_keycloak_not_called()

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_ENABLED, MIDDLEWARE=claims_middleware())
    def test_superuser_with_claims_not_admin__denied(self):
        self.client.force_login(self.superuser)

        with self.assertLogs("accounts.audit", level="WARNING") as logs:
            response = self.client.get(
                self.export_url,
                {"month": "2026-09", "kind": "logins"},
                headers={"Authorization": bearer("admin", roles=["editor"])},
            )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response["Location"], reverse("wagtailadmin_home"))
        self.assertIn("hub-users access denied user=admin", logs.output[0])
        self.assert_keycloak_not_called()

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_page__previous_month_selected_and_no_keycloak_calls(self):
        self.client.force_login(self.superuser)

        response = self.client.get(self.page_url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, f'<form method="get" action="{self.export_url}"')
        self.assertContains(response, '<option value="2026-09" selected>September 2026</option>', html=True)
        self.assertContains(response, "October 2026 (to date)")
        self.assertContains(response, '<button type="submit" name="kind" value="logins" class="button">')
        self.assertContains(response, 'name="kind" value="users"')
        self.assertContains(response, f'href="{reverse("hub_users_index")}"')
        self.assert_keycloak_not_called()

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export_logins__csv_with_headers_guard_and_audit(self):
        self.client.force_login(self.superuser)

        with self.assertLogs("accounts.audit", level="INFO") as logs:
            response = self.client.get(self.export_url, {"month": "2026-09", "kind": "logins"})
            body = response.content.decode()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Content-Type"], "text/csv; charset=utf-8")
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="eodh-hub-logins-2026-09.csv"')
        self.assertIn("no-store", response["Cache-Control"])
        self.assertEqual(response["X-Content-Type-Options"], "nosniff")
        self.assertEqual(
            body.splitlines(),
            [
                "login_time_utc,user_id,username,email,first_name,last_name,identity_provider,client_id,"
                "new_user,first_login_of_new_user,registered_via,account_created_utc,user_deleted",
                "2026-09-02T10:01:00Z,id-gone,'-gone,,,,,portal,true,true,form,,true",
                "2026-09-03T08:00:00Z,id-1,'=cmd,cmd@example.com,'+Plus,,github,portal,false,false,,2024-01-02T03:04:05Z,false",
                "2026-09-04T08:00:00Z,id-1,'=cmd,cmd@example.com,'+Plus,,,notebooks,false,false,,2024-01-02T03:04:05Z,false",
            ],
        )
        self.get_client.return_value.iter_events.assert_called_once_with(
            start=datetime(2026, 9, 1, tzinfo=UTC), end=datetime(2026, 10, 1, tzinfo=UTC)
        )
        self.assertIn("hub-users login-activity export by user=admin month=2026-09 kind=logins rows=3", logs.output[0])

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export_users__one_row_per_user(self):
        self.client.force_login(self.superuser)

        with self.assertLogs("accounts.audit", level="INFO") as logs:
            response = self.client.get(self.export_url, {"month": "2026-09", "kind": "users"})

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="eodh-hub-login-users-2026-09.csv"')
        self.assertEqual(
            response.content.decode().splitlines(),
            [
                "user_id,username,email,first_name,last_name,new_user,account_created_utc,login_count,"
                "first_login_utc,last_login_utc,identity_providers,clients,user_deleted",
                "id-gone,'-gone,,,,true,,1,2026-09-02T10:01:00Z,2026-09-02T10:01:00Z,,portal,true",
                "id-1,'=cmd,cmd@example.com,'+Plus,,false,2024-01-02T03:04:05Z,2,"
                "2026-09-03T08:00:00Z,2026-09-04T08:00:00Z,github,portal;notebooks,false",
            ],
        )
        self.assertIn("kind=users rows=2", logs.output[0])

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__invalid_month__400_without_keycloak_call(self):
        self.client.force_login(self.superuser)

        for params in (
            {"month": "2026-13", "kind": "logins"},
            {"month": "2024-01", "kind": "logins"},
            {"kind": "logins"},
        ):
            with self.subTest(params=params):
                response = self.client.get(self.export_url, params)

                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
                self.assertEqual(response.content, b"Invalid month.")
                self.assertNotIn("Content-Disposition", response)
        self.assert_keycloak_not_called()

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__invalid_kind__400_without_keycloak_call(self):
        self.client.force_login(self.superuser)

        response = self.client.get(self.export_url, {"month": "2026-09", "kind": "everything"})

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assert_keycloak_not_called()

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__keycloak_error__502_not_truncated_csv(self):
        self.client.force_login(self.superuser)

        def events_then_error():
            yield EVENTS[0]
            raise KeycloakAdminUnavailable("down")

        cases = (
            (
                "iter_events",
                KeycloakAdminAuthError("forbidden"),
                b"The identity service refused access to login events.",
            ),
            ("iter_events", events_then_error(), b"Could not reach the identity service."),
            ("iter_users", KeycloakAdminUnavailable("down"), b"Could not reach the identity service."),
        )
        for method, failure, message in cases:
            with self.subTest(method=method, failure=failure):
                self.get_client.return_value = fake_client()
                if isinstance(failure, Exception):
                    getattr(self.get_client.return_value, method).side_effect = failure
                else:
                    getattr(self.get_client.return_value, method).return_value = failure

                with self.assertNoLogs("accounts.audit", level="INFO"):
                    response = self.client.get(self.export_url, {"month": "2026-09", "kind": "logins"})

                self.assertEqual(response.status_code, HTTPStatus.BAD_GATEWAY)
                self.assertEqual(response.content, message)
                self.assertNotIn("Content-Disposition", response)

    @override_settings(KEYCLOAK=KEYCLOAK_ENABLED, OIDC_CLAIMS=OIDC_CLAIMS_DISABLED)
    def test_export__times_in_utc_regardless_of_profile_timezone(self):
        profile = UserProfile.get_for_user(self.superuser)
        profile.current_time_zone = "Pacific/Auckland"
        profile.save()
        self.client.force_login(self.superuser)

        response = self.client.get(self.export_url, {"month": "2026-09", "kind": "logins"})

        self.assertContains(response, "2026-09-03T08:00:00Z")
        self.assertNotContains(response, "2026-09-03T20:00")
