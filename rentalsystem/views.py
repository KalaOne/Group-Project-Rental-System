from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from .forms import *
from .models import *


def index(request):
    if request.user.is_authenticated:
        return home(request)
    return landing(request)


def home(request):
    context = {
        'items': Item.objects.all(),
        'categories': Category.objects.all()
    }
    return render(request, "rentalsystem/home.html", context)


def landing(request):
    return render(request, "rentalsystem/landing.html")


def profile(request):
    return render(request, 'profile.html')


class SignUp(generic.CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'rentalsystem/signup.html'


