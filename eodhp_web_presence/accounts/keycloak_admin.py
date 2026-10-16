import base64
import logging
import time
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlencode

import urllib3
from django.conf import settings

logger = logging.getLogger(__name__)

LAST_LOGIN_ATTRIBUTE = "lastLoginTime"


def _last_login(values: Sequence[object]) -> datetime | None:
    times = []
    for value in values:
        if not str(value).isdecimal():
            continue
        try:
            times.append(datetime.fromtimestamp(int(value) / 1000, tz=UTC))
        except (OverflowError, OSError, ValueError):
            continue
    return max(times, default=None)


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
    last_login: datetime | None = None

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
            last_login=_last_login((data.get("attributes") or {}).get(LAST_LOGIN_ATTRIBUTE) or []),
        )


@dataclass(frozen=True)
class HubEvent:
    id: str | None
    type: str
    time: datetime
    user_id: str | None
    client_id: str | None
    identity_provider: str | None
    register_method: str | None
    username: str | None

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> "HubEvent":
        details = data.get("details") or {}
        return cls(
            id=data.get("id") or None,
            type=str(data.get("type", "")),
            time=datetime.fromtimestamp(data.get("time", 0) / 1000, tz=UTC),
            user_id=data.get("userId") or None,
            client_id=data.get("clientId") or None,
            identity_provider=details.get("identity_provider") or None,
            register_method=details.get("register_method") or None,
            username=details.get("username") or None,
        )


Params = Mapping[str, str] | Sequence[tuple[str, str]]


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

    @property
    def events_url(self) -> str:
        return f"{self.base_url}/admin/realms/{self.realm}/events"

    def count_users(self, search: str | None = None) -> int:
        params = {"search": search} if search else {}
        return int(self._get(f"{self.users_url}/count", params).json())

    def list_users(self, *, search: str | None = None, first: int = 0, max: int | None = None) -> list[HubUser]:
        params: dict[str, str] = {
            "briefRepresentation": "false",
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

    def iter_events(
        self, *, start: datetime, end: datetime, types: Sequence[str] = ("LOGIN", "REGISTER")
    ) -> Iterator[HubEvent]:
        types_params = [("type", event_type) for event_type in types]
        cursor_ms = int(start.timestamp() * 1000)
        # dateTo is inclusive, so stop a millisecond short of the half-open end
        end_ms = int(end.timestamp() * 1000) - 1
        # Keycloak orders by time only, so offset paging can skip or repeat events that share a millisecond.
        # Page by time instead: restart each page at the last event's millisecond and drop the ones already seen.
        seen: set[str | HubEvent] = set()
        while True:
            params = [
                *types_params,
                ("dateFrom", str(cursor_ms)),
                ("dateTo", str(end_ms)),
                ("direction", "asc"),
                ("first", "0"),
                ("max", str(self.page_size)),
            ]
            page = self._get(self.events_url, params).json()
            for item in page:
                event = HubEvent.from_json(item)
                key = event.id if event.id is not None else event
                if key not in seen:
                    seen.add(key)
                    yield event
            if len(page) < self.page_size:
                return
            last_ms = int(page[-1]["time"])
            if last_ms == cursor_ms:
                # A whole page in one millisecond would fetch the same page forever
                raise KeycloakAdminError(f"At least {self.page_size} events at {cursor_ms} ms; raise the page size")
            cursor_ms = last_ms

    def _get(self, url: str, params: Params) -> urllib3.BaseHTTPResponse:
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

    def _request(self, url: str, params: Params, token: str) -> urllib3.BaseHTTPResponse:
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
