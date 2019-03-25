from django.urls import path

from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('landing/', TemplateView.as_view(template_name='landing.html'), name='landing'),
    path('add_category/', views.add_category, name='add_category'),
]