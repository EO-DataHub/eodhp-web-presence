import logging
from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import Group
from django.http import HttpRequest

from .models import User
from .tokens import UserClaims

logger = logging.getLogger(__name__)


class ClaimsBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, **kwargs) -> Optional[User]:
        if not hasattr(request, "claims"):
            return None  # No OIDC claims attached to request

        claims: UserClaims = request.claims

        if not claims.username:
            return None  # User is not authenticated

        # Claims present and user is authenticated
        user, created = User.objects.get_or_create(username=claims.username, is_active=True)
        if created:
            user.set_unusable_password()
            user.save()

        if not user.is_active:
            logger.warning(
                "User '%s' is not active. They may have issues performing some actions.", user
            )

        # Check admin status
        if claims.admin != user.is_superuser or claims.admin != user.is_staff:
            user.is_superuser = claims.admin
            user.is_staff = claims.admin
            user.save()

        user_groups = {
            group.name: group for group in user.groups.filter(name__in=["Moderators", "Editors"])
        }
        # Check moderator status
        if claims.moderator != ("Moderators" in user_groups):
            if claims.moderator:
                user.groups.add(Group.objects.get(name="Moderators"))
            else:
                user.groups.remove(user_groups["Moderators"])
        # Check editor status
        if claims.editor != ("Editors" in user_groups):
            if claims.editor:
                user.groups.add(Group.objects.get(name="Editors"))
            else:
                user.groups.remove(user_groups["Editors"])

        logger.debug(
            "User '%s' authenticated (created=%s, admin=%s, moderator=%s, editor=%s)",
            user,
            created,
            claims.admin,
            claims.moderator,
            claims.editor,
        )
        return user

    def get_user(self, user_id: int) -> Optional[User]:
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
