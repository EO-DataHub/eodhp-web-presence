import csv
import io
import logging
from collections.abc import Iterable, Sequence
from datetime import UTC, date, datetime
from urllib.parse import quote, urlencode

from django import forms
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from wagtail.admin.forms.search import SearchForm

from .csv_utils import csv_cell
from .keycloak_admin import HubUser, KeycloakAdminAuthError, KeycloakAdminError, get_client
from .login_activity import (
    LOGIN_COLUMNS,
    PER_USER_COLUMNS,
    aggregate_per_user,
    build_login_rows,
    month_choices,
    month_window,
    previous_month,
)
from .permissions import hub_admin_required

logger = logging.getLogger(__name__)
audit_logger = logging.getLogger("accounts.audit")

USERS_PER_PAGE = 50
CSV_COLUMNS = ("id", "username", "email", "email_verified", "first_name", "last_name", "enabled", "created")


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

    # Fetch everything first so a Keycloak failure gives an error, not a short CSV that looks complete
    try:
        users = list(client.iter_users(search=search or None))
    except KeycloakAdminError:
        logger.exception("Could not export hub users")
        return HttpResponse("Could not reach the identity service.", status=502, content_type="text/plain")

    audit_logger.info("hub-users export by user=%s search=%r rows=%d", username, search, len(users))
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return _csv_response(CSV_COLUMNS, (csv_row(user) for user in users), f"eodh-hub-users-{stamp}.csv")


class LoginActivityForm(forms.Form):
    month = forms.ChoiceField(label="Month")
    kind = forms.ChoiceField(choices=[("logins", "Logins"), ("users", "Per user")])

    def __init__(self, *args: object, today: date, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.fields["month"].choices = month_choices(today)


@hub_admin_required
def hub_users_login_activity(request: HttpRequest) -> HttpResponse:
    if get_client() is None:
        raise Http404
    today = datetime.now(UTC).date()
    form = LoginActivityForm(initial={"month": previous_month(today)}, today=today)

    return render(
        request,
        "accounts/hub_users/login_activity.html",
        {
            "page_title": "Login activity",
            "header_title": "Login activity",
            "header_icon": "history",
            "form": form,
            "hub_users_url": reverse("hub_users_index"),
        },
    )


@hub_admin_required
def hub_users_login_activity_export(request: HttpRequest) -> HttpResponse:
    client = get_client()
    if client is None:
        raise Http404
    form = LoginActivityForm(request.GET, today=datetime.now(UTC).date())
    if not form.is_valid():
        message = "Invalid month." if "month" in form.errors else "Invalid export type."
        return HttpResponse(message, status=400, content_type="text/plain")
    month = form.cleaned_data["month"]
    kind = form.cleaned_data["kind"]
    start, end = month_window(month)
    username = request.user.get_username()

    # Fetch everything first so a Keycloak failure gives an error, not a short CSV that looks complete
    try:
        events = list(client.iter_events(start=start, end=end))
        users = {user.id: user for user in client.iter_users()}
    except KeycloakAdminAuthError:
        logger.exception("Keycloak refused access to login events")
        return HttpResponse(
            "The identity service refused access to login events.", status=502, content_type="text/plain"
        )
    except KeycloakAdminError:
        logger.exception("Could not export login activity")
        return HttpResponse("Could not reach the identity service.", status=502, content_type="text/plain")

    rows = build_login_rows(events, users, start, end)
    columns, filename = LOGIN_COLUMNS, f"eodh-hub-logins-{month}.csv"
    if kind == "users":
        rows = aggregate_per_user(rows)
        columns, filename = PER_USER_COLUMNS, f"eodh-hub-login-users-{month}.csv"

    audit_logger.info(
        "hub-users login-activity export by user=%s month=%s kind=%s rows=%d", username, month, kind, len(rows)
    )
    return _csv_response(columns, ([csv_cell(row[column]) for column in columns] for row in rows), filename)


def _csv_response(header: Sequence[str], rows: Iterable[Sequence[str]], filename: str) -> HttpResponse:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(header)
    writer.writerows(rows)

    response = HttpResponse(buffer.getvalue(), content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response["Cache-Control"] = "no-store"
    response["X-Content-Type-Options"] = "nosniff"
    return response
