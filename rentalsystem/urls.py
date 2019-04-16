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
    path('jobstats/', views.jobstats, name='jobstats'),
    path('postItem/', views.UserPostItem.as_view(), name='postItem'),
    path('post_item_details/<int:pk>', views.UserPostItem.post_item_details, name='post_item_details'),
    path('item_details/<int:pk>', views.ItemDetails.as_view(), name='item_details'),
]
