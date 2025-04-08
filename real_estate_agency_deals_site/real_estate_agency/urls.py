from real_estate_agency import views
from real_estate_agency import utils
from django.urls import path


urlpatterns_actions = [
    path('del-review-agency/<int:pk>/', utils.del_review_agency, name='del_review_agency'),
    path('del-realtor/<int:pk>/', utils.del_realtor, name='del_realtor'),
]

urlpatterns = ([
    path('review/<int:pk>/change/', views.ChangeReviewAgencyView.as_view(), name='review_change'),

    path('realtor-list/', views.RealtorListView.as_view(), name='realtor_list'),
    path('realtor-new/', views.NewRealtorView.as_view(), name='realtor_new'),
    path('realtor/<int:pk>/', views.RealtorView.as_view(), name='realtor'),
    path('realtor/<int:pk>/change/', views.ChangeRealtorView.as_view(), name='realtor_change'),
]
+ urlpatterns_actions
)
