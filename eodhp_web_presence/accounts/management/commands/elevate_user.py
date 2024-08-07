from django.core.management.base import BaseCommand

from ...models import User


class Command(BaseCommand):
    help = "Elevate a user to have admin privileges"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username of the user to elevate")
        parser.add_argument(
            "--revoke", action="store_true", help="Revoke admin privileges instead of elevating"
        )

    def handle(self, username: str, revoke: bool = False, *args, **kwargs):
        self.stdout.write("Finding user...")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR("User not found"))
            raise

        if revoke:
            self.revoke_user(user)
        else:
            self.elevate_user(user)

    def elevate_user(self, user: User):
        user.is_staff = True
        user.is_superuser = True
        try:
            user.save()
        except Exception:
            self.stdout.write(self.style.ERROR("Could not update user"))
            raise
        else:
            self.stdout.write(self.style.SUCCESS(f"User {user.username} elevated to admin"))

    def revoke_user(self, user: User):
        user.is_staff = False
        user.is_superuser = False
        try:
            user.save()
        except Exception:
            self.stdout.write(self.style.ERROR("Could not update user"))
            raise
        else:
            self.stdout.write(self.style.SUCCESS(f"User {user.username} admin access revoked"))
