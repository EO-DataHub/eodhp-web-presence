import jwt
from django.test import TestCase
from django.test.utils import override_settings

from .. import tokens


@override_settings(
    OIDC_CLAIMS={
        "ENABLED": True,
        "USERNAME_PATH": "username",
        "EMAIL_PATH": "email",
        "ROLES_PATH": "roles",
        "SUPERUSER_ROLE": "admin",
        "MODERATOR_ROLE": "moderator",
        "EDITOR_ROLE": "editor",
    }
)
class TestTokens(TestCase):
    def test_extract_claims__valid_token__success(self):
        bearer_token = "Bearer " + jwt.encode(
            {
                "username": "test-user",
                "email": "test-user@email.com",
            },
            "secret",
            algorithm="HS256",
        )
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(username="test-user", email="test-user@email.com", admin=False),
        )

    def test_extract_claims__valid_admin_token__success(self):
        bearer_token = "Bearer " + jwt.encode(
            {
                "username": "test-user",
                "email": "test-user@email.com",
                "roles": ["admin"],
            },
            "secret",
            algorithm="HS256",
        )
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(username="test-user", email="test-user@email.com", admin=True),
        )

    def test_extract_claims__no_header__empty_claims(self):
        bearer_token = None
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(),
        )

    def test_extract_claims__username_is_empty_str__username_is_none(self):
        bearer_token = "Bearer " + jwt.encode(
            {
                "username": "",
            },
            "secret",
            algorithm="HS256",
        )
        claims = tokens.extract_claims(bearer_token)
        self.assertIsNone(claims.username)

    def test_extract_claims__invalid_token__empty_claims(self):
        bearer_token = "Bearer invalid_token"
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(),
        )

    @override_settings(
        OIDC_CLAIMS={
            "USERNAME_PATH": None,
            "EMAIL_PATH": None,
            "ROLES_PATH": None,
            "ADMIN_ROLE": None,
        }
    )
    def test_extract_claims__settings_omitted__empty_claims(self):
        bearer_token = "Bearer " + jwt.encode(
            {
                "username": "test-user",
                "email": "test-user@email.com",
            },
            "secret",
            algorithm="HS256",
        )
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(),
        )

    def test_extract_field__valid_key__success(self):
        claims = {
            "username": "test-user",
        }
        self.assertEqual(
            tokens._extract_field("username", claims),
            "test-user",
        )

    def test_extract_field__valid_key_email__success(self):
        claims = {
            "email": "test-user@email.com",
        }
        self.assertEqual(
            tokens._extract_field("email", claims),
            "test-user@email.com",
        )

    def test_extract_field__nested_valid_key__success(self):
        claims = {
            "info": {
                "profile": {
                    "username": "test-user",
                },
            }
        }
        self.assertEqual(
            tokens._extract_field("info.profile.username", claims),
            "test-user",
        )

    def test_extract_field__missing_key__return_none(self):
        claims = {
            "user": "test-user",
        }
        self.assertEqual(
            tokens._extract_field("username", claims),  # username field does not exist
            None,
        )
