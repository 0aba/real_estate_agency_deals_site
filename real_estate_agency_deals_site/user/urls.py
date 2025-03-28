from user import endpoints_micro_api
from django.urls import path
from user import utils
from user import views


urlpatterns_actions_micro_api = [
    path('notifications/<int:notification_id>/view/', endpoints_micro_api.mark_notification_viewed, name='mark_notification_viewed'),
    path('notifications/<int:notification_id>/del/', endpoints_micro_api.delete_notification, name='del_notification'),
]

urlpatterns_actions = [
    path('logout/', utils.logout_action, name='logout'),
    path('ban/<slug:username>/', utils.ban_user_action, name='ban'),
    path('unban/<slug:username>/', utils.unban_user_action, name='unban'),

    path('add-bl-profile/<slug:username>/', utils.create_bl_action_router(
        utils.bl_add_action,
        **utils.routes_profile,
    ), name='add_bl_profile'),
    path('del-bl-profile/<slug:username>/', utils.create_bl_action_router(
        utils.bl_del_action,
        **utils.routes_profile,
    ), name='del_bl_profile'),
    path('del-bl-my-list/<slug:username>/', utils.create_bl_action_router(
        utils.bl_del_action,
        **utils.routes_my_list,
    ), name='del_bl_my_black_list'),

    path('disable-account/', utils.disable_account_action, name='disable_account'),
    path('del-private-message/<int:pk>/', utils.del_private_message, name='del_private_message'),
]

urlpatterns = ([
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('email-confirmation/', views.EmailConfirmationView.as_view(), name='email_confirmation'),
    path('login/', views.MyLoginView.as_view(), name='login'),
    path('create-restore-password/', views.CreateRestorePasswordView.as_view(), name='create_restore_password'),
    path('restore-info/', views.RestoreInfoView.as_view(), name='restore_info'),
    path('restore-confirmation/<uuid:code>/', views.RestorePasswordView.as_view(), name='restore_confirmation'),
    path('profile/<slug:username>/', views.ProfileUserView.as_view(), name='user_profile'),
    path('profile/<slug:username>/change/', views.ChangeProfileUserView.as_view(), name='user_profile_change'),
    path('my-black-list/', views.BlackListUserView.as_view(), name='my_black_list'),

    path('private-message/', views.PrivateMessageView.as_view(), name='private_message'),
    path('private-message/<slug:username>/', views.PrivateMessageUserView.as_view(), name='private_message_user'),
    path('private-message/<int:pk>/change/', views.ChangePrivateMessageView.as_view(), name='private_message_change'),
]
+ urlpatterns_actions
+ urlpatterns_actions_micro_api
)
