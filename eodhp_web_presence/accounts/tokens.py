import logging
import re
from dataclasses import dataclass

import jwt
from django.conf import settings

logger = logging.getLogger(__name__)


CLAIMS_KEY_PATTERN = re.compile(r"(?<!\\)\.")  # delimit on '.' but not '\.'


@dataclass(frozen=True)
class UserClaims:
    username: str | None = None
    admin: bool = False


ClaimsDict = dict[str, "ClaimsField"]
ClaimsField = str | float | int | bool | list["ClaimsField"] | ClaimsDict | None


def extract_claims(auth_header: str | None) -> UserClaims:
    if auth_header is None:
        return UserClaims()

    token = auth_header.removeprefix("Bearer ")
    try:
        data: dict[str, str | dict] = jwt.decode(
            token, options={"verify_signature": False}, algorithms=["HS256"]
        )
    except (jwt.DecodeError, jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
        return UserClaims()

    # Extract claims from the token, validate types
    username = _extract_field(settings.OIDC_CLAIMS["USERNAME_PATH"], data)
    if not isinstance(username, str):
        logger.warning(
            "Username '%s' is not str type ('%s'). Username ignored.", username, type(username)
        )
        username = None

    roles: list[str] = (
        _extract_field(settings.OIDC_CLAIMS["ROLES_PATH"], data) or []
    )  # if None then convert to empty list
    if not isinstance(roles, list):
        logger.warning("Roles '%s' is not list type ('%s'). Roles ignored.", roles, type(roles))
        roles: list[str] = []
    try:
        is_admin = (
            settings.OIDC_CLAIMS["ADMIN_ROLE"] and settings.OIDC_CLAIMS["ADMIN_ROLE"] in roles
        )
    except (TypeError, KeyError):
        logger.warning(
            "Admin role %s not found. Error parsing roles %s.",
            settings.OIDC_CLAIMS["ADMIN_ROLE"],
            roles,
        )
        is_admin = False

    return UserClaims(
        username=username or None,  # empty str should result in username=None for consistency
        admin=is_admin,
    )


def _extract_field(key_path: str, claims: ClaimsDict) -> ClaimsField:
    r"""
    Extract a field from a nested dictionary using a key pattern. Separate nested keys
    with '.'. Use '\.' to escape a literal '.' in a key.
    """
    value: ClaimsField = claims
    for key in CLAIMS_KEY_PATTERN.split(key_path):
        try:
            value: ClaimsField = value[key]
        except (KeyError, TypeError):
            logger.warning("Key %s not found in %s", key_path, claims)
            return None
    return value
