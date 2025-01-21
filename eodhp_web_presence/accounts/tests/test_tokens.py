import jwt
from django.test import TestCase
from django.test.utils import override_settings

from .. import tokens


@override_settings(
    OIDC_CLAIMS={
        "USERNAME_PATH": "username",
        "ROLES_PATH": "roles",
        "ADMIN_ROLE": "admin",
    }
)
class TestTokens(TestCase):
    def test_extract_claims__valid_token__success(self):
        bearer_token = "Bearer " + jwt.encode(
            {
                "username": "test-user",
            },
            "secret",
            algorithm="HS256",
        )
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(username="test-user", admin=False),
        )

    def test_extract_claims__valid_admin_token__success(self):
        bearer_token = "Bearer " + jwt.encode(
            {
                "username": "test-user",
                "roles": ["admin"],
            },
            "secret",
            algorithm="HS256",
        )
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(username="test-user", admin=True),
        )

    def test_extract_claims__no_header__empty_claims(self):
        bearer_token = None
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(),
        )

    def test_extract_claims__invalid_token__empty_claims(self):
        bearer_token = "Bearer invalid_token"
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
