from django.conf.urls.static import static
from django.urls import path, include
from django.contrib import admin
from django.conf import settings


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('common.urls')),
    path('user/', include('user.urls')),
    path('staff/', include('staff.urls')),
    path('real-estate-agency/', include('real_estate_agency.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
