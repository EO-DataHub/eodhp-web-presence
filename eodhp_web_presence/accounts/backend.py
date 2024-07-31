from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from django.http import HttpRequest


class AuthBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, username: Optional[str] = None) -> Optional[User]:
        if username is not None:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_unusable_password()
                user.save()
            return user
        else:
            return None

    def get_user(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
