from dataclasses import dataclass, field

import jwt


@dataclass(frozen=True)
class UserClaims:
    username: str | None = None
    roles: list[str] = field(default_factory=list)


def extract_claims(auth_header: str | None) -> UserClaims:
    if auth_header is None:
        return UserClaims()

    token = auth_header.removeprefix("Bearer ")
    data: dict[str, str | dict] = jwt.decode(
        token, options={"verify_signature": False}, algorithms=["HS256"]
    )

    return UserClaims(
        username=data.get("preferred_username", None),
        roles=data.get("realm_access", {}).get("roles", []),
    )
