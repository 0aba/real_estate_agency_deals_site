from real_estate_agency import views
from real_estate_agency import utils
from django.urls import path


urlpatterns_actions = [
    path('del-review-agency/<int:pk>/', utils.del_review_agency, name='del_review_agency'),
    path('del-realtor/<int:pk>/', utils.del_realtor, name='del_realtor'),
]

urlpatterns = ([
    path('signup-agency/', views.SignupRealEstateAgencyView.as_view(), name='signup_agency'),
    path('agency/<slug:slug_name>/', views.ProfileRealEstateAgencyView.as_view(), name='agency_profile'),
    path('agency/<slug:slug_name>/change/', views.ChangeProfileRealEstateAgencyView.as_view(), name='agency_profile_change'),
    path('review/<int:pk>/change/', views.ChangeReviewAgencyView.as_view(), name='review_change'),

    path('realtor-list/', views.RealtorListView.as_view(), name='realtor_list'),
    path('realtor-new/', views.NewRealtorView.as_view(), name='realtor_new'),
    path('realtor/<int:pk>/', views.RealtorView.as_view(), name='realtor'),
    path('realtor/<int:pk>/change/', views.ChangeRealtorView.as_view(), name='review_change'),
]
+ urlpatterns_actions
)
