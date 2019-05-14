from django.urls import path

from . import views
from django.views.generic.base import TemplateView

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name = 'about'),
    path('landing/', views.landing, name='landing'),
    path('myjobs/', views.myjobs, name='myjobs'),
    path('my_orders/', views.my_orders, name='my_orders'),
    path('profile/', views.profile, name='profile'),
    path('home_search/', views.home_search, name='home_search'),
    path('jobstats/', views.jobstats, name='jobstats'),
    path('postItem/', views.user_post_item, name='user_post_item'),
    path('item_details/', views.post_item_details, name="item_details"),
    path('post_item_complete/', views.post_item_complete, name="post_item_complete"),
    path('leave_review/',views.leave_review, name="leave_review"),
    path('create_transaction/', views.createTrans, name='create_transaction'),
    path('item_listings/', views.item_listings, name='item_listings'),
    path('review_confirmation/',views.review_confirmation, name="review_confirmation"),
    path('confirm_transaction/', views.confirm_transaction, name='confirm_transaction'),
    path('edit_account/', views.account_settings, name='edit_account'),
    path('rent_item/', views.rent_item, name='rent_item'),
    path('account_details/', views.account_details, name='account_details'),
    path('leave/', views.profile, name='leave'),
    path('upload_pic/', views.upload_pic, name='upload_pic'),
    path('my_listings/', views.my_listings, name='my_listings'),
    path('confirm_return/', views.confirm_return, name='confirm_return'),

]
