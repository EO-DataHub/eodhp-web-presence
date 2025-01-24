from django.contrib import auth
from django.contrib.auth.models import Group
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

    def test_authenticate__promote_user_to_editor__return_none(self):
        existing_user = models.User.objects.create(username="test-user")
        request = factory.get("/")
        request.claims = UserClaims(username="test-user", editor=True)

        self.assertFalse(existing_user.groups.filter(name="Moderators").exists())
        self.assertFalse(existing_user.groups.filter(name="Editors").exists())

        user = auth.authenticate(request=request)

        self.assertIsInstance(user, models.User)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.groups.filter(name="Moderators").exists())
        self.assertTrue(user.groups.filter(name="Editors").exists())

    def test_authenticate__demote_user_from_moderator__return_none(self):
        existing_user = models.User.objects.create(username="test-user")
        existing_user.groups.add(Group.objects.get(name="Moderators"))
        existing_user.groups.add(Group.objects.get(name="Editors"))

        request = factory.get("/")
        request.claims = UserClaims(username="test-user", editor=True)

        self.assertTrue(existing_user.groups.filter(name="Moderators").exists())
        self.assertTrue(existing_user.groups.filter(name="Editors").exists())

        user = auth.authenticate(request=request)

        self.assertIsInstance(user, models.User)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.groups.filter(name="Moderators").exists())
        self.assertTrue(user.groups.filter(name="Editors").exists())
