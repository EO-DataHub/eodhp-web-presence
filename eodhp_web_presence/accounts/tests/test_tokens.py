import jwt
from django.test import TestCase

from .. import tokens


class TestTokens(TestCase):
    def test_extract_claims__valid_token__success(self):
        bearer_token = "Bearer " + jwt.encode(
            {
                "preferred_username": "test-user",
                "realm_access": {
                    "roles": ["test_role"],
                },
            },
            "secret",
            algorithm="HS256",
        )
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(username="test-user", roles=["test_role"]),
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
