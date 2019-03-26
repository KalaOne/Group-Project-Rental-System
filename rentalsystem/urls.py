from django.urls import path

from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('home/', views.home, name='home'),
    path('landing/', views.landing, name='landing'),
]