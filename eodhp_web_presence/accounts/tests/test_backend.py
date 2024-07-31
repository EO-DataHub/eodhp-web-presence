from django.test import TestCase

from .. import backend, models


class TestBackend(TestCase):
    def setUp(self):
        self.backend = backend.AuthBackend()

    def test_authenticate__existing_user__return_existing_user(self):
        existing_user = models.User.objects.create(username="test-user")
        user = self.backend.authenticate(request=object(), username="test-user")
        self.assertIsInstance(user, models.User)
        self.assertEqual(existing_user, user)

    def test_authenticate__new_user__return_new_user(self):
        user = self.backend.authenticate(request=object(), username="test-user")
        self.assertIsInstance(user, models.User)
        self.assertIsNotNone(user)

        new_user = models.User.objects.get(username="test-user")
        self.assertEqual(new_user, user)

    def test_authenticate__username_is_none__return_none(self):
        user = self.backend.authenticate(request=object(), username=None)
        self.assertIsNone(user)

    def test_get_user__existing_user__return_existing_user(self):
        existing_user = models.User.objects.create(username="test-user")
        user = self.backend.get_user(existing_user.pk)
        self.assertIsInstance(user, models.User)
        self.assertEqual(existing_user, user)

    def test_get_user__nonexistent_user__return_none(self):
        user = self.backend.get_user(1)
        self.assertIsNone(user)
