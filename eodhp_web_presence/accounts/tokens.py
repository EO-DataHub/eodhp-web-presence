import logging
import re
from dataclasses import dataclass
from functools import lru_cache

import jwt
from django.conf import settings
from jwt import PyJWKClient, PyJWTError

logger = logging.getLogger(__name__)


CLAIMS_KEY_PATTERN = re.compile(r"(?<!\\)\.")  # delimit on '.' but not '\.'

# The client IDs tokens for this platform are actually issued under, per the reference
# implementation in eodh-ac-api/wf-catalogue-service/accounting-service. The deployment's
# configured client ID (settings.KEYCLOAK["CLIENT_ID"]) is always included too, in case it
# differs from this reference list.
_REFERENCE_AUDIENCE = ["oauth2-proxy-workspaces", "oauth2-proxy", "account"]


def _jwt_audience() -> list[str]:
    return list(dict.fromkeys([settings.KEYCLOAK["CLIENT_ID"], *_REFERENCE_AUDIENCE]))


@lru_cache
def _jwks_client() -> PyJWKClient:
    """One client per process, so the JWKS document is cached rather than re-fetched from
    Keycloak on every request. PyJWKClient does this caching internally, but only across
    calls on the same instance.
    """
    return PyJWKClient(settings.KEYCLOAK["CERTS_URL"])


@dataclass(frozen=True)
class UserClaims:
    username: str | None = None
    email: str | None = None
    admin: bool = False
    moderator: bool = False
    editor: bool = False

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "username": self.username,
            "email": self.email,
            "admin": self.admin,
            "moderator": self.moderator,
            "editor": self.editor,
        }


ClaimsDict = dict[str, "ClaimsField"]
ClaimsField = str | float | int | bool | list["ClaimsField"] | ClaimsDict | None


def extract_claims(auth_header: str | None) -> UserClaims:
    if auth_header is None:
        return UserClaims()

    token = auth_header.removeprefix("Bearer ")
    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token)
        data: dict[str, str | dict] = jwt.decode(
            token,
            signing_key.key,
            audience=_jwt_audience(),
            algorithms=["RS256"],
        )
    except PyJWTError:
        logger.warning("JWT signature verification failed", exc_info=True)
        return UserClaims()

    # Extract claims from the token, validate types
    username = _extract_field(settings.OIDC_CLAIMS["USERNAME_PATH"], data)
    if not username or not isinstance(username, str):
        logger.warning("Username '%s' is not str type ('%s'). Username ignored.", username, type(username))
        return UserClaims()

    email = _extract_field(settings.OIDC_CLAIMS["EMAIL_PATH"], data)
    if not email or not isinstance(email, str):
        logger.warning("Email '%s' is not str type ('%s'). Email ignored.", email, type(email))
        return UserClaims()

    roles: list[str] = (
        _extract_field(settings.OIDC_CLAIMS["ROLES_PATH"], data) or []
    )  # if None then convert to empty list
    if not isinstance(roles, list):
        roles: list[str] = []

    permissions = {
        claim: True
        for claim, role in (
            ("admin", settings.OIDC_CLAIMS["SUPERUSER_ROLE"]),
            ("moderator", settings.OIDC_CLAIMS["MODERATOR_ROLE"]),
            ("editor", settings.OIDC_CLAIMS["EDITOR_ROLE"]),
        )
        if role in roles
    }

    return UserClaims(username=username, email=email, **permissions)


def _extract_field(key_path: str, claims: ClaimsDict) -> ClaimsField:
    r"""
    Extract a field from a nested dictionary using a key pattern. Separate nested keys
    with '.'. Use '\.' to escape a literal '.' in a key.
    """
    if not key_path or not isinstance(key_path, str):
        return None

    value: ClaimsField = claims
    for key in CLAIMS_KEY_PATTERN.split(key_path):
        try:
            value: ClaimsField = value[key]
        except (KeyError, TypeError):
            logger.warning("Key %s not found in %s", key_path, claims)
            return None
    return value
