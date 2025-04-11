from real_estate_agency import views
from real_estate_agency import utils
from django.urls import path


urlpatterns_actions = [
    path('del-review-agency/<int:pk>/', utils.del_review_agency, name='del_review_agency'),
    path('del-realtor/<int:pk>/', utils.del_realtor, name='del_realtor'),

    path('del-real-estate/<int:pk>/', utils.del_real_estate, name='del_real_estate'),
]

urlpatterns = ([
    path('review/<int:pk>/change/', views.ChangeReviewAgencyView.as_view(), name='review_change'),

    path('realtor-list/', views.RealtorListView.as_view(), name='realtor_list'),
    path('realtor-new/', views.NewRealtorView.as_view(), name='realtor_new'),
    path('realtor/<int:pk>/', views.RealtorView.as_view(), name='realtor'),
    path('realtor/<int:pk>/change/', views.ChangeRealtorView.as_view(), name='realtor_change'),

    path('real-estate-list/', views.RealEstateListView.as_view(), name='real_estate_list'),
    path('real-estate-new/', views.NewRealEstateView.as_view(), name='real_estate_new'),
    path('real-estate/<int:pk>/', views.RealEstateView.as_view(), name='real_estate'),
    path('real-estate/<int:pk>/change/', views.ChangeRealEstateView.as_view(), name='real_estate_change'),
]
+ urlpatterns_actions
)
