from real_estate_agency import views
from real_estate_agency import utils
from django.urls import path


urlpatterns_actions = [
    path('del-review-agency/<int:pk>/', utils.del_review_agency, name='del_review_agency'),
    path('del-realtor/<int:pk>/', utils.del_realtor, name='del_realtor'),

    path('del-real-estate/<int:pk>/', utils.del_real_estate, name='del_real_estate'),

    path('del-deal/<slug:title_slug>/', utils.del_deal, name='del_deal'),

    path('del-deal/<slug:title_slug>/', utils.reject_deal, name='reject_deal'),

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
    path('re-creation-deal/', views.ReCreationDealView.as_view(), name='re_creation_deal'),
    path('deal/<slug:title_slug>/', views.DealView.as_view(), name='deal'),
    path('deal/<slug:title_slug>/change/', views.ChangeDealView.as_view(), name='deal_change'),

    path('start-deal/<slug:title_slug>/', views.StartDeal.as_view(), name='start_deal'),
    path('start-deal/<slug:title_slug>/', views.SuccessDeal.as_view(), name='success_deal'),

    path('my-track-deal-list/', views.TrackDealView.as_view(), name='my_track_deal_list'),

    path('deal-statistics/', views.DealStatistics.as_view(), name='deal_statistics'),
    path('real-estate-data-import/', views.ImportRealEstateData.as_view(), name='real_estate_data_import'),
    path('realtor-data-import/', views.ImportRealtorData.as_view(), name='realtor_data_import'),
]
+ urlpatterns_actions
)
