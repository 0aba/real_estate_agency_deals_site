from django.urls import path
from user import views


urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('email-confirmation/', views.EmailConfirmationView.as_view(), name='email_confirmation'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('create-restore-password/', views.CreateRestorePasswordView.as_view(), name='create_restore_password'),
    path('restore-info/', views.RestoreInfoView.as_view(), name='restore_info'),
    path('restore-confirmation/<uuid:code>/', views.RestorePasswordView.as_view(), name='restore_confirmation'),
    path('logout', views.logout_page, name='logout'),

    # path('profile/<slag:username>/', views.ProfileUserView.as_view(), name='profile'),
]
