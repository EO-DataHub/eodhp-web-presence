import environ
from django.http import HttpResponse
from django.views.decorators.http import require_GET

env = environ.Env()
IS_PROD = env("IS_PROD", default=False)


@require_GET
def robots_txt(request):
    return HttpResponse(robots_txt_file, content_type="text/plain")


if IS_PROD:
    robots_txt_file = """\
User-agent: *
Disallow:
"""
else:
    robots_txt_file = """\
User-Agent: *
Disallow: /
"""
