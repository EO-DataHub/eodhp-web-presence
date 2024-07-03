from django.http import HttpResponse
from django.template.loader import render_to_string

from .models import SupportTopicPage


def search_topics(request):
    query = request.GET.get("query", "")

    if query:
        search_results = SupportTopicPage.objects.live().autocomplete(query)
    else:
        search_results = SupportTopicPage.objects.live().all()

    html = render_to_string("home/search_results.html", {"support_topics": search_results})

    return HttpResponse(html)


def search_topics_blank(request):
    query = request.GET.get("query", "")

    if query:
        search_results = SupportTopicPage.objects.live().autocomplete(query)
    else:
        search_results = None

    for s in search_results:
        s.slug = s.url_path.removeprefix("/home")

    html = render_to_string("home/search_results.html", {"support_topics": search_results})

    return HttpResponse(html)
