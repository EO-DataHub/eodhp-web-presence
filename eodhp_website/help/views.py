from django.http import HttpResponse
from django.shortcuts import render


def help_page_view(request):
    context = {"helppages": ['a', 'b']}
    return render(request, 'help/help_page.html', context=context)
