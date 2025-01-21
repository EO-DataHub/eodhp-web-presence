import logging
from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.http import HttpRequest

from .models import User
from .tokens import UserClaims

logger = logging.getLogger(__name__)


class ClaimsBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, **kwargs) -> Optional[User]:
        if not hasattr(request, "claims"):
            # No OIDC claims attached to request
            return None

        claims: UserClaims = request.claims

        if not claims.username:
            # User is not authenticated
            return None

        # Claims present and user is authenticated
        user, created = User.objects.get_or_create(username=claims.username)
        if created:
            user.set_unusable_password()
            user.save()

        # Check admin status
        if claims.admin != user.is_staff:
            user.is_staff = claims.admin
            user.save()

        logger.debug("User %s authenticated (created=%s, admin=%s)", user, created, claims.admin)
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
