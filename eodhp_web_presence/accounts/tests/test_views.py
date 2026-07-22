from urllib.parse import quote

from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from ..models import User

KEYCLOAK_SETTINGS = {
    "CLIENT_ID": "test-client",
    "AUTH_URL": "https://keycloak.example.com/realms/test/protocol/openid-connect/auth",
    "OAUTH2_PROXY_SIGNIN": "https://proxy.example.com/oauth2/start",
    "OAUTH2_PROXY_SIGNOUT": "https://proxy.example.com/oauth2/sign_out",
    "KC_ACTION_REDIRECT_URL": None,
}


@override_settings(KEYCLOAK=KEYCLOAK_SETTINGS, WAGTAIL_CACHE=False)
class KeycloakActionViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(username="test-user")

    def test_update_email__redirects_to_keycloak_with_kc_action(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("keycloak_action", args=["update_email"]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            response.url.startswith("https://keycloak.example.com/realms/test/protocol/openid-connect/auth?")
        )
        self.assertIn("response_type=code", response.url)
        self.assertIn("scope=openid", response.url)
        self.assertIn("client_id=test-client", response.url)
        self.assertIn("kc_action=UPDATE_EMAIL", response.url)
        self.assertIn("state=", response.url)

    def test_update_email__redirect_uri_defaults_to_callback(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("keycloak_action", args=["update_email"]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "redirect_uri=http%3A%2F%2Ftestserver%2Faccounts%2Fkc-action%2Fcallback%2F",
            response.url,
        )

    def test_update_profile__redirects_to_keycloak_with_kc_action(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("keycloak_action", args=["update_profile"]))

        self.assertEqual(response.status_code, 302)
        self.assertIn("kc_action=UPDATE_PROFILE", response.url)

    def test_unknown_action__redirects_to_accounts_page(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("keycloak_action", args=["delete_account"]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/")

    def test_unauthenticated__redirects_to_sign_in_view(self):
        response = self.client.get(reverse("keycloak_action", args=["update_email"]))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/sign_in/"))
        self.assertIn("next=/accounts/kc-action/update_email/", response.url)

    @override_settings(
        KEYCLOAK={
            **KEYCLOAK_SETTINGS,
            "KC_ACTION_REDIRECT_URL": "https://hub.example.com/accounts/",
        }
    )
    def test_configured_redirect_url__used_as_redirect_uri(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("keycloak_action", args=["update_email"]))

        self.assertEqual(response.status_code, 302)
        self.assertIn("redirect_uri=https%3A%2F%2Fhub.example.com%2Faccounts%2F", response.url)


@override_settings(KEYCLOAK=KEYCLOAK_SETTINGS, WAGTAIL_CACHE=False)
class KeycloakActionCallbackViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def set_action_state(self, state: str = "test-state") -> None:
        session = self.client.session
        session["keycloak_action_state"] = state
        session.save()

    def test_callback__restarts_proxy_session_to_refresh_claims(self):
        self.set_action_state()

        response = self.client.get(
            reverse("keycloak_action_callback"),
            {"code": "test-code", "state": "test-state"},
        )

        self.assertEqual(response.status_code, 302)
        expected_sign_in = f"https://proxy.example.com/oauth2/start?rd={quote('http://testserver/accounts/')}"
        self.assertEqual(
            response.url,
            f"https://proxy.example.com/oauth2/sign_out?rd={quote(expected_sign_in)}",
        )

    def test_callback__invalid_state__returns_to_accounts(self):
        self.set_action_state()

        response = self.client.get(
            reverse("keycloak_action_callback"),
            {"code": "test-code", "state": "wrong-state"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/")

    def test_callback__missing_code__returns_to_accounts(self):
        self.set_action_state()

        response = self.client.get(reverse("keycloak_action_callback"), {"state": "test-state"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/")


@override_settings(KEYCLOAK=KEYCLOAK_SETTINGS, WAGTAIL_CACHE=False)
class SignInViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()

    def test_sign_in__next_param__redirects_back_to_next(self):
        response = self.client.get(reverse("sign_in"), {"next": "/accounts/"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://proxy.example.com/oauth2/start?rd=/accounts/")

    def test_sign_in__external_next_param__ignored(self):
        response = self.client.get(reverse("sign_in"), {"next": "https://evil.example.com/steal"})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://proxy.example.com/oauth2/start")

    def test_sign_in__referer_used_when_no_next(self):
        response = self.client.get(
            reverse("sign_in"),
            headers={"referer": "http://testserver/workspaces/"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "https://proxy.example.com/oauth2/start?rd=http%3A//testserver/workspaces/",
        )

    def test_sign_in__external_referer__ignored(self):
        response = self.client.get(
            reverse("sign_in"),
            headers={"referer": "https://evil.example.com/steal"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "https://proxy.example.com/oauth2/start")
