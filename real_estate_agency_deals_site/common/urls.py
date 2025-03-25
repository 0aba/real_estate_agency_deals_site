from django.urls import path
from common import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
]
