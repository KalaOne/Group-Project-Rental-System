from django.urls import path

from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('home/', views.home, name='home'),
    path('landing/', views.landing, name='landing'),
    path('myjobs/', views.myjobs, name='myjobs'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('profile/', views.profile, name='profile'),
    path('home_search/', views.home_search, name='home_search'),
    path('jobstats/', views.jobstats, name='jobstats'),
    path('postItem/', views.UserPostItem.as_view(), name='postItem'),
    path('post_item_details/<int:pk>', views.item_details, name="post_item_details"),
    path('leave_review/',views.leave_review, name="leave_review"),
    path('create_transaction/', views.createTrans, name='create_transaction'),


    path('item_listings/', views.item_listings, name='item_listings'),

]
