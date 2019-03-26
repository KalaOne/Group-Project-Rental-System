from django.urls import path

from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('home/', TemplateView.as_view(template_name='home.html'), name='home'),
    path('landing/', TemplateView.as_view(template_name='landing.html'), name='landing'),
]