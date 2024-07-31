from dataclasses import dataclass, field
from http import HTTPStatus
from unittest import mock

import jwt
from django.http import HttpRequest, HttpResponse
from django.test import RequestFactory, TestCase

from ..middleware import AuthMiddleware

factory = RequestFactory()


@dataclass(frozen=True)
class HTTPRequestMock:
    path: str = "/"
    headers: dict[str, str] = field(default_factory=dict)


class TestMiddleware(TestCase):
    @mock.patch.object(AuthMiddleware, "is_allowed", return_value=True)
    def test_authorized_path__unauthenticated__return_200(self, _: mock.MagicMock):
        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = factory.get("/")
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @mock.patch.object(AuthMiddleware, "is_allowed", return_value=True)
    def test_authorized_path__authenticated__return_200(self, _: mock.MagicMock):
        bearer_token = "Bearer " + jwt.encode(
            {
                "preferred_username": "test-user",
                "realm_access": {
                    "roles": ["hub_user"],
                },
            },
            "secret",
            algorithm="HS256",
        )

        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = factory.get("/", headers={"Authorization": bearer_token})
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    @mock.patch.object(AuthMiddleware, "is_allowed", return_value=False)
    def test_unauthorized_path__unauthenticated__return_401(self, _: mock.MagicMock):
        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock()
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    @mock.patch.object(AuthMiddleware, "is_allowed", return_value=False)
    def test_unauthorized_path__authenticated__return_403(self, _: mock.MagicMock):
        bearer_token = "Bearer " + jwt.encode(
            {
                "preferred_username": "test-user",
                "realm_access": {
                    "roles": ["not_a_hub_user"],
                },
            },
            "secret",
            algorithm="HS256",
        )

        get_response = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        mw = AuthMiddleware(get_response=get_response)
        request = HTTPRequestMock(headers={"Authorization": bearer_token})
        response = mw(request)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
