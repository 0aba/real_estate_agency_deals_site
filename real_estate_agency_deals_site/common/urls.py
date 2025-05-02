from django.urls import path
from common import views


urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('user-agreement/', views.UserAgreement.as_view(), name='user_agreement'),
]
