from django.urls import path
from staff import views


urlpatterns = [
    path('complaint/new/', views.NewComplaint.as_view(), name='complaint_new'),
    path('complaint-list/', views.ComplaintList.as_view(), name='complaint_list'),
    path('complaint/<int:pk>/consider/', views.ConsiderComplaint.as_view(), name='complaint_consider'),

    path('appeal/new/', views.NewAppeal.as_view(), name='appeal_new'),
    path('appeal-list/', views.AppealList.as_view(), name='appeal_list'),
    path('appeal/<int:pk>/consider/', views.ConsiderAppeal.as_view(), name='appeal_consider'),

    path('logs-private-message/', views.LogsPrivateMessage.as_view(), name='logs_private_message'),

    path('deal-statistics/', views.DealStatistics.as_view(), name='deal_statistics'),
]
