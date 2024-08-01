import logging
from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest

from .models import User

logger = logging.getLogger(__name__)


class ClaimsBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, **kwargs) -> Optional[User]:
        if hasattr(request, "claims") and request.claims.username is not None:
            user, created = User.objects.get_or_create(username=request.claims.username)
            if created:
                user.set_unusable_password()
                user.save()
            logger.debug("User %s authenticated (created=%s)", user, created)
            return user
        else:
            return None

    def get_user(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
