from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_info, name='api_info'),
    path('register', views.register_customer, name='register_customer'),
]