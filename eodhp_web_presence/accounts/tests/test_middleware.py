from http import HTTPStatus
from unittest import mock

import jwt
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from ..middleware import ClaimsMiddleware, OPAAuthorizationMiddleware
from ..models import User
from ..tokens import UserClaims

factory = RequestFactory()


def create_bearer_token():
    return "Bearer " + jwt.encode(
        {
            "preferred_username": "test-user",
            "realm_access": {
                "roles": ["hub_user"],
            },
        },
        "secret",
        algorithm="HS256",
    )


class ClaimsMiddlewareTestCase(TestCase):
    def setUp(self):
        self.view = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        self.middleware = SessionMiddleware(
            get_response=AuthenticationMiddleware(
                get_response=ClaimsMiddleware(
                    get_response=self.view,
                )
            )
        )

    def test_call__valid_token__auth(self):
        bearer_token = create_bearer_token()
        request = factory.get("/", headers={"Authorization": bearer_token})

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            request.claims,
            UserClaims(
                username="test-user",
                roles=["hub_user"],
            ),
        )
        self.assertIsInstance(request.user, User)
        self.assertIsNotNone(User.objects.get(username="test-user"))

    def test_call__invalid_token__no_auth(self):
        request = factory.get("/", headers={"Authorization": "Bearer invalid_token"})

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(request.claims, UserClaims())
        self.assertIsInstance(request.user, AnonymousUser)

    def test_call__no_auth_header__no_auth(self):
        request = factory.get("/")

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(request.claims, UserClaims())
        self.assertIsInstance(request.user, AnonymousUser)

    def test_call__auth_user_no_header__log_out(self):
        user = User.objects.create_user(username="test-user")
        request = factory.get("/", user=user)

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(request.claims, UserClaims())
        self.assertIsInstance(request.user, AnonymousUser)

    def test_call__auth_user_doesnt_match_claims__log_in_claims_user(self):
        auth_user = User.objects.create_user(username="user-1")
        bearer_token = create_bearer_token()
        request = factory.get("/", user=auth_user, headers={"Authorization": bearer_token})

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(request.claims.username, "test-user")
        self.assertEqual(request.user.username, "test-user")


@mock.patch.object(OPAAuthorizationMiddleware, "is_allowed")
class OPAAuthorizationMiddlewareTestCase(TestCase):
    def setUp(self):
        self.view = mock.MagicMock(return_value=HttpResponse("OK", status=200))
        self.middleware = SessionMiddleware(
            get_response=AuthenticationMiddleware(
                get_response=ClaimsMiddleware(
                    get_response=OPAAuthorizationMiddleware(
                        self.view, opa_client_url="http://localhost:8181"
                    ),
                )
            )
        )

    def test_authorized_path__unauthenticated__return_200(self, is_allowed: mock.MagicMock):
        request = factory.get("/")
        is_allowed.return_value = True

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_authorized_path__authenticated__return_200(self, is_allowed: mock.MagicMock):
        bearer_token = create_bearer_token()
        request = factory.get("/", headers={"Authorization": bearer_token})
        is_allowed.return_value = True

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unauthorized_path__unauthenticated__return_401(self, is_allowed: mock.MagicMock):
        request = factory.get("/")
        is_allowed.return_value = False

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    def test_unauthorized_path__authenticated__return_403(self, is_allowed: mock.MagicMock):
        bearer_token = create_bearer_token()
        request = factory.get("/", headers={"Authorization": bearer_token})
        is_allowed.return_value = False

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
