from http import HTTPStatus
from unittest import mock

import jwt
from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings

from ..middleware import ClaimsMiddleware
from ..models import User
from ..tokens import UserClaims

factory = RequestFactory()


@override_settings(
    OIDC_CLAIMS={
        "ENABLED": True,
        "USERNAME_PATH": "username",
        "EMAIL_PATH": "email",
        "ROLES_PATH": "roles",
        "SUPERUSER_ROLE": "admin",
        "MODERATOR_ROLE": "moderator",
        "EDITOR_ROLE": "editor",
    }
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
        auth_header = "Bearer " + jwt.encode(
            {
                "username": "test-user",
                "email": "test-user@email.com",
            },
            "secret",
            algorithm="HS256",
        )
        request = factory.get("/", headers={"Authorization": auth_header})

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            request.claims,
            UserClaims(username="test-user", email="test-user@email.com"),
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
        auth_header = "Bearer " + jwt.encode(
            {
                "username": "test-user",
                "email": "test-user@email.com",
            },
            "secret",
            algorithm="HS256",
        )
        request = factory.get("/", user=auth_user, headers={"Authorization": auth_header})

        response = self.middleware(request)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(request.claims.username, "test-user")
        self.assertEqual(request.user.username, "test-user")
