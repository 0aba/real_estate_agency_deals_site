from real_estate_agency import views
from real_estate_agency import utils
from django.urls import path


urlpatterns_actions = [
    path('del-review-agency/<int:pk>/', utils.del_review_agency, name='del_review_agency'),
    path('del-realtor/<int:pk>/', utils.del_realtor, name='del_realtor'),

    path('del-real-estate/<int:pk>/', utils.del_real_estate, name='del_real_estate'),

    path('del-deal/<slug:title_slug>/', utils.del_deal, name='del_deal'),
    path('completed-deal/<slug:title_slug>/', utils.completed_deal, name='completed_deal'),
    path('make-rented-deal/<slug:title_slug>/', utils.make_rented_deal, name='make_rented_deal'),
    path('make-unrented-deal/<slug:title_slug>/', utils.make_unrented_deal, name='make_unrented_deal'),
    path('track-deal/<slug:title_slug>/', utils.track_deal, name='track_deal'),
    path('stop-track-deal/<slug:title_slug>/', utils.stop_track_deal, name='stop_track_deal'),
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

    path('deal-list/', views.DealListView.as_view(), name='deal_list'),
    path('deal-new/', views.NewDealView.as_view(), name='deal_new'),
    path('deal/<slug:title_slug>/', views.DealView.as_view(), name='deal'),
    path('deal/<slug:title_slug>/change/', views.ChangeDealView.as_view(), name='deal_change'),
]
+ urlpatterns_actions
)
