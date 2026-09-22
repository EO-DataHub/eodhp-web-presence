import csv
import logging
from collections.abc import Iterator
from datetime import UTC, datetime
from urllib.parse import quote, urlencode

from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from wagtail.admin.forms.search import SearchForm

from .keycloak_admin import HubUser, KeycloakAdminError, get_client
from .permissions import hub_admin_required

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("accounts.audit")

USERS_PER_PAGE = 50
CSV_COLUMNS = ("id", "username", "email", "email_verified", "first_name", "last_name", "enabled", "created")
FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def sign_in(request: HttpRequest) -> HttpResponseRedirect:
    referer = request.headers.get("Referer")

    redirect_tag = f"?rd={quote(referer)}" if referer else ""

    return redirect(f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNIN']}{redirect_tag}")


def sign_out(request: HttpRequest) -> HttpResponseRedirect:
    keycloak_logout_url = (
        f"{settings.KEYCLOAK['LOGOUT_URL']}"
        f"?client_id={settings.KEYCLOAK['CLIENT_ID']}"
        f"&post_logout_redirect_uri={quote(settings.KEYCLOAK['LOGOUT_REDIRECT_URL'])}"
    )

    oauth2_proxy_logout_url = f"{settings.KEYCLOAK['OAUTH2_PROXY_SIGNOUT']}?rd={quote(keycloak_logout_url)}"

    return redirect(oauth2_proxy_logout_url)


@hub_admin_required
def hub_users_index(request: HttpRequest) -> HttpResponse:
    client = get_client()
    if client is None:
        raise Http404
    search_form = SearchForm(request.GET, placeholder="Search users")
    search = search_form.data.get("q", "").strip()

    users: list[HubUser] = []
    total = 0
    try:
        total = client.count_users(search=search or None)
        page = Paginator(range(total), USERS_PER_PAGE).get_page(request.GET.get("p"))
        if total:
            users = client.list_users(search=search or None, first=page.start_index() - 1, max=USERS_PER_PAGE)
    except KeycloakAdminError:
        logger.exception("Could not list hub users")
        messages.error(request, "Could not reach the identity service. Try again later.")
        page = Paginator([], USERS_PER_PAGE).get_page(1)

    export_url = reverse("hub_users_export")
    if search:
        export_url += "?" + urlencode({"q": search})

    return render(
        request,
        "accounts/hub_users/index.html",
        {
            "page_title": "Hub users",
            "header_title": "Hub users",
            "header_icon": "group",
            "search_form": search_form,
            "search": search,
            "query_parameters": urlencode({"q": search}) if search else "",
            "users": users,
            "total": total,
            "page": page,
            "export_url": export_url,
        },
    )


class Echo:
    def write(self, value: str) -> str:
        return value


def csv_cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    text = str(value)
    # Stop spreadsheets from evaluating user-supplied cells as formulas
    if text.startswith(FORMULA_PREFIXES):
        return "'" + text
    return text


def csv_row(user: HubUser) -> list[str]:
    return [
        csv_cell(user.id),
        csv_cell(user.username),
        csv_cell(user.email),
        csv_cell(user.email_verified),
        csv_cell(user.first_name),
        csv_cell(user.last_name),
        csv_cell(user.enabled),
        csv_cell(user.created),
    ]


@hub_admin_required
def hub_users_export(request: HttpRequest) -> HttpResponse:
    client = get_client()
    if client is None:
        raise Http404
    search = request.GET.get("q", "").strip()
    username = request.user.get_username()

    try:
        users = client.iter_users(search=search or None)
        first_user = next(users, None)
    except KeycloakAdminError:
        logger.exception("Could not export hub users")
        return HttpResponse("Could not reach the identity service.", status=502, content_type="text/plain")

    def rows() -> Iterator[str]:
        writer = csv.writer(Echo())
        count = 0
        yield writer.writerow(CSV_COLUMNS)
        try:
            for user in [first_user] if first_user else []:
                count += 1
                yield writer.writerow(csv_row(user))
            for user in users:
                count += 1
                yield writer.writerow(csv_row(user))
        except KeycloakAdminError:
            logger.exception("Hub users export interrupted after %d rows", count)
        finally:
            audit_logger.info("hub-users export by user=%s search=%r rows=%d", username, search, count)

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    response = StreamingHttpResponse(rows(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="eodh-hub-users-{stamp}.csv"'
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
