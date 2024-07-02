from django.http import HttpResponse
from django.template.loader import render_to_string
from wagtail.search.models import Query
from .models import SupportTopicPage

def search_topics(request):
    query = request.GET.get('query', '')

    if query:
        search_results = SupportTopicPage.objects.live().search(query)
    else:
        search_results = SupportTopicPage.objects.live().all()

    html = render_to_string('home/search_results.html', {'support_topics': search_results})

    return HttpResponse(html)
