from django.contrib import auth
from django.test import RequestFactory, TestCase

from .. import models
from ..tokens import UserClaims

factory = RequestFactory()


class ClaimsBackendTestCase(TestCase):
    def test_authenticate__existing_user__return_existing_user(self):
        existing_user = models.User.objects.create(username="test-user")
        request = factory.get("/")
        request.claims = UserClaims(username="test-user")

        user = auth.authenticate(request=request)

        self.assertIsInstance(user, models.User)
        self.assertEqual(existing_user, user)

    def test_authenticate__new_user__return_new_user(self):
        request = factory.get("/")
        request.claims = UserClaims(username="test-user")

        user = auth.authenticate(request=request)

        self.assertIsInstance(user, models.User)
        self.assertIsNotNone(user)

        new_user = models.User.objects.get(username="test-user")
        self.assertEqual(new_user, user)

    def test_authenticate__username_is_none__return_none(self):
        request = factory.get("/")
        request.claims = UserClaims()

        user = auth.authenticate(request=request)

        self.assertIsNone(user)

    def test_authenticate__username_is_empty_str__return_none(self):
        request = factory.get("/")
        request.claims = UserClaims(username="")

        user = auth.authenticate(request=request)

        self.assertIsNone(user)
