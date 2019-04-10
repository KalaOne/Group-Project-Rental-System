from django.urls import path

from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('home/', views.home, name='home'),
    path('landing/', views.landing, name='landing'),
    path('myjobs/', views.myjobs, name='myjobs'),
    path('myjobs/jobcomp/', views.myjobs, name='myjobsupdate'),
    path('profile/', views.profile, name='profile'),

    path('home_search/', views.home_search),
]
