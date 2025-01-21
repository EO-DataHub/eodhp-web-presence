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
    moderator: bool = False
    editor: bool = False

    def to_dict(self) -> dict[str, str | bool]:
        return {
            "username": self.username,
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
        data: dict[str, str | dict] = jwt.decode(
            token, options={"verify_signature": False}, algorithms=["HS256"]
        )
    except (jwt.DecodeError, jwt.ExpiredSignatureError, jwt.InvalidSignatureError):
        return UserClaims()

    # Extract claims from the token, validate types
    username = _extract_field(settings.OIDC_CLAIMS["USERNAME_PATH"], data)
    if not username or not isinstance(username, str):
        logger.warning(
            "Username '%s' is not str type ('%s'). Username ignored.", username, type(username)
        )
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

    return UserClaims(username=username, **permissions)


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
