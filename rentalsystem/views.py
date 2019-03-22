from django.shortcuts import render
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/landing')
    return TemplateResponse(request, "home.html")

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'