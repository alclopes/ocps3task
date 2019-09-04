from django.utils import translation
from django.shortcuts import render, redirect
from django.conf import settings


def index(request):
    if request.LANGUAGE_CODE:
        context = {'LANGUAGE_CODE': request.LANGUAGE_CODE}
    else:
        context = {'LANGUAGE_CODE': request.session[translation.LANGUAGE_SESSION_KEY]}
    return render(request, 'languages/index.html', context)


def set_language_from_url(request, user_language):
    if user_language == 'pt':
        user_language = 'pt-br'
    translation.activate(user_language)
    request.session[translation.LANGUAGE_SESSION_KEY] = user_language
    return redirect('core:home')
