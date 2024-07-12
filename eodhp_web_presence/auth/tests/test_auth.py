from dataclasses import dataclass, field
from http import HTTPStatus
from unittest import mock

from django.http import HttpResponse
from django.test import TestCase

from .. import AuthMiddleware


@dataclass(frozen=True)
class HTTPRequestMock:
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)


class TestAuthMiddleware(TestCase):
    @mock.patch("auth.is_allowed", return_value=True)
    def test_authorized_path__unauthenticated__return_200(self, _: mock.MagicMock):
        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock()
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @mock.patch("auth.is_allowed", return_value=True)
    def test_authorized_path__authenticated__return_200(self, _: mock.MagicMock):
        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock(headers={"Authorization": "Bearer token"})
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
    def test_unauthorized_path__authenticated__return_401(self, _: mock.MagicMock):
        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock(headers={"Authorization": "Bearer token"})
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
