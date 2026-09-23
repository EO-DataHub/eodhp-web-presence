"""Shared helpers for signing test JWTs and standing in for Keycloak's JWKS endpoint.

extract_claims() now verifies signatures against a real PyJWKClient, so tests need a
throwaway RSA keypair to sign with and a mocked _jwks_client() to hand back its public half,
rather than calling out to a real Keycloak instance over the network.
"""

import types
from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey

from .. import tokens

PRIVATE_KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def sign_token(key: RSAPrivateKey = PRIVATE_KEY, aud: str = "eodh", **claims: object) -> str:
    return jwt.encode({"aud": aud, **claims}, key, algorithm="RS256")


@contextmanager
def mock_jwks(key: RSAPrivateKey = PRIVATE_KEY) -> Iterator[None]:
    """Stands in for a real call to Keycloak: hands back our own throwaway public key."""
    with patch.object(tokens, "_jwks_client") as mock_client:
        mock_client.return_value.get_signing_key_from_jwt.return_value = types.SimpleNamespace(key=key.public_key())
        yield
