from dataclasses import dataclass, field
from http import HTTPStatus
from unittest import mock

import jwt
from django.http import HttpResponse
from django.test import TestCase

from .. import AuthMiddleware, extract_roles


@dataclass(frozen=True)
class HTTPRequestMock:
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)


class TestAuthMiddleware(TestCase):
    def test_extract_roles__valid_token__success(self):
        roles = ["valid_role"]
        bearer_token = jwt.encode(
            {
                "realm_access": {
                    "roles": roles,
                }
            },
            "secret",
            algorithm="HS256",
        )

        assert extract_roles(bearer_token) == roles

    def test_extract_roles__valid_token_no_roles__success(self):
        bearer_token = jwt.encode({"realm_access": {}}, "secret", algorithm="HS256")

        assert extract_roles(bearer_token) == []

    def test_extract_roles__valid_token_no_realm__success(self):
        bearer_token = jwt.encode({}, "secret", algorithm="HS256")

        assert extract_roles(bearer_token) == []

    @mock.patch("auth.is_allowed", return_value=True)
    def test_authorized_path__unauthenticated__return_200(self, _: mock.MagicMock):
        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock()
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @mock.patch("auth.is_allowed", return_value=True)
    def test_authorized_path__authenticated__return_200(self, _: mock.MagicMock):
        bearer_token = jwt.encode(
            {
                "realm_access": {
                    "roles": ["hub_user"],
                }
            },
            "secret",
            algorithm="HS256",
        )

        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock(headers={"Authorization": bearer_token})
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @mock.patch("auth.is_allowed", return_value=False)
    def test_unauthorized_path__unauthenticated__return_401(self, _: mock.MagicMock):
        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock()
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    @mock.patch("auth.is_allowed", return_value=False)
    def test_unauthorized_path__authenticated__return_403(self, _: mock.MagicMock):
        bearer_token = jwt.encode(
            {
                "realm_access": {
                    "roles": ["not_a_hub_user"],
                }
            },
            "secret",
            algorithm="HS256",
        )

        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock(headers={"Authorization": bearer_token})
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
