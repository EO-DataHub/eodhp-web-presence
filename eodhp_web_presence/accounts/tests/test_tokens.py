import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from django.test import TestCase
from django.test.utils import override_settings

from .. import tokens
from .jwt_helpers import mock_jwks, sign_token


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
    def setUp(self):
        self._mock_jwks = mock_jwks()
        self._mock_jwks.__enter__()
        self.addCleanup(self._mock_jwks.__exit__, None, None, None)

    def test_extract_claims__valid_token__success(self):
        bearer_token = "Bearer " + sign_token(
            username="test-user",
            email="test-user@email.com",
        )
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(username="test-user", email="test-user@email.com", admin=False),
        )

    def test_extract_claims__valid_admin_token__success(self):
        bearer_token = "Bearer " + sign_token(
            username="test-user",
            email="test-user@email.com",
            roles=["admin"],
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
        bearer_token = "Bearer " + sign_token(username="")
        claims = tokens.extract_claims(bearer_token)
        self.assertIsNone(claims.username)

    def test_extract_claims__invalid_token__empty_claims(self):
        bearer_token = "Bearer invalid_token"
        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(),
        )

    def test_extract_claims__forged_signature__empty_claims(self):
        """This is the exact bug that shipped: verify_signature was False, so any signature -
        including one that is not cryptographically valid at all - was accepted.
        """
        header = jwt.utils.base64url_encode(b'{"alg":"RS256","typ":"JWT"}').decode()
        payload = jwt.utils.base64url_encode(b'{"username":"attacker","roles":["admin"],"aud":"eodh"}').decode()
        forged_signature = jwt.utils.base64url_encode(b"not-a-real-signature").decode()
        forged_token = "Bearer " + f"{header}.{payload}.{forged_signature}"

        self.assertEqual(
            tokens.extract_claims(forged_token),
            tokens.UserClaims(),
        )

    def test_extract_claims__signed_by_a_different_key__empty_claims(self):
        """Guards against accepting any valid-looking signature rather than specifically
        Keycloak's: a token signed end-to-end correctly, just with the wrong key.
        """
        other_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        bearer_token = "Bearer " + sign_token(key=other_key, username="test-user")

        self.assertEqual(
            tokens.extract_claims(bearer_token),
            tokens.UserClaims(),
        )

    def test_extract_claims__wrong_audience__empty_claims(self):
        bearer_token = "Bearer " + sign_token(aud="some-other-client", username="test-user")

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
        bearer_token = "Bearer " + sign_token(
            username="test-user",
            email="test-user@email.com",
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
