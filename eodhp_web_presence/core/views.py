from django.http import HttpResponse
from django.views.decorators.http import require_GET


@require_GET
def authenticated(request):
    return HttpResponse(
        "If you can view this, your account has the correct roles", content_type="text/plain"
    )
