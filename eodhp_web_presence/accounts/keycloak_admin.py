import base64
import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import urllib3
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class HubUser:
    id: str
    username: str
    email: str | None
    email_verified: bool
    first_name: str | None
    last_name: str | None
    enabled: bool
    created: datetime | None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "HubUser":
        created_ms = data.get("createdTimestamp")
        return cls(
            id=str(data.get("id", "")),
            username=str(data.get("username", "")),
            email=data.get("email") or None,
            email_verified=bool(data.get("emailVerified", False)),
            first_name=data.get("firstName") or None,
            last_name=data.get("lastName") or None,
            enabled=bool(data.get("enabled", False)),
            created=datetime.fromtimestamp(created_ms / 1000, tz=UTC) if created_ms is not None else None,
        )


class KeycloakAdminError(Exception):
    pass


class KeycloakAdminAuthError(KeycloakAdminError):
    pass


class KeycloakAdminUnavailable(KeycloakAdminError):
    pass


class KeycloakAdminClient:
    TOKEN_EXPIRY_MARGIN = 30.0

    def __init__(
        self,
        *,
        base_url: str,
        realm: str,
        client_id: str,
        client_secret: str,
        timeout: float = 10.0,
        page_size: int = 200,
        http: urllib3.PoolManager | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.realm = realm
        self.page_size = page_size
        self._client_id = client_id
        self._client_secret = client_secret
        self._http = http or urllib3.PoolManager(timeout=urllib3.Timeout(total=timeout), retries=False)
        self._token: str | None = None
        self._token_expires_at = 0.0

    @property
    def token_url(self) -> str:
        return f"{self.base_url}/realms/{self.realm}/protocol/openid-connect/token"

    @property
    def users_url(self) -> str:
        return f"{self.base_url}/admin/realms/{self.realm}/users"

    def count_users(self, search: str | None = None) -> int:
        params = {"search": search} if search else {}
        return int(self._get(f"{self.users_url}/count", params).json())

    def list_users(self, *, search: str | None = None, first: int = 0, max: int | None = None) -> list[HubUser]:
        params: dict[str, str] = {
            "briefRepresentation": "true",
            "first": str(first),
            "max": str(max if max is not None else self.page_size),
        }
        if search:
            params["search"] = search
        users = [HubUser.from_json(item) for item in self._get(self.users_url, params).json()]
        return sorted(users, key=lambda user: user.username)

    def iter_users(self, *, search: str | None = None) -> Iterator[HubUser]:
        first = 0
        while True:
            page = self.list_users(search=search, first=first, max=self.page_size)
            yield from page
            if len(page) < self.page_size:
                return
            first += self.page_size

    def _get(self, url: str, params: dict[str, str]) -> urllib3.BaseHTTPResponse:
        response = self._request(url, params, self._get_token())
        if response.status == 401:
            response = self._request(url, params, self._get_token(force=True))
        if response.status in (401, 403):
            raise KeycloakAdminAuthError(f"Keycloak admin API returned {response.status} for {url}")
        if response.status >= 500:
            raise KeycloakAdminUnavailable(f"Keycloak admin API returned {response.status} for {url}")
        if response.status != 200:
            raise KeycloakAdminError(f"Keycloak admin API returned {response.status} for {url}")
        return response

    def _request(self, url: str, params: dict[str, str], token: str) -> urllib3.BaseHTTPResponse:
        try:
            return self._http.request(
                "GET",
                url,
                fields=params,
                headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            )
        except urllib3.exceptions.HTTPError as exc:
            logger.error("Keycloak admin API request to %s failed: %s", url, type(exc).__name__)
            raise KeycloakAdminUnavailable(f"Keycloak admin API request to {url} failed") from exc

    def _get_token(self, *, force: bool = False) -> str:
        if not force and self._token and time.monotonic() < self._token_expires_at:
            return self._token
        credentials = base64.b64encode(f"{self._client_id}:{self._client_secret}".encode()).decode()
        try:
            response = self._http.request(
                "POST",
                self.token_url,
                body=urlencode({"grant_type": "client_credentials"}),
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
            )
        except urllib3.exceptions.HTTPError as exc:
            logger.error("Keycloak token request failed: %s", type(exc).__name__)
            raise KeycloakAdminUnavailable("Keycloak token request failed") from exc
        if response.status >= 500:
            raise KeycloakAdminUnavailable(f"Keycloak token endpoint returned {response.status}")
        if response.status != 200:
            logger.error("Keycloak token endpoint returned %s", response.status)
            raise KeycloakAdminAuthError(f"Keycloak token endpoint returned {response.status}")
        data = response.json()
        self._token = str(data["access_token"])
        self._token_expires_at = time.monotonic() + float(data.get("expires_in", 60)) - self.TOKEN_EXPIRY_MARGIN
        return self._token


def get_client() -> KeycloakAdminClient | None:
    config = settings.KEYCLOAK
    if not config.get("USER_LIST_ENABLED"):
        return None
    return KeycloakAdminClient(
        base_url=config["ADMIN_BASE_URL"],
        realm=config["REALM"],
        client_id=config["ADMIN_CLIENT_ID"],
        client_secret=config["ADMIN_CLIENT_SECRET"],
        timeout=config["ADMIN_TIMEOUT"],
        page_size=config["ADMIN_PAGE_SIZE"],
    )
