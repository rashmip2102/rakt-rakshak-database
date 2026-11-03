from django.contrib import admin
from django.urls import path
from apps.matching.views import SpatialMatchAPIView
from apps.dispatch.views import ReserveInventoryAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/matching/find/', SpatialMatchAPIView.as_view(), name='spatial-matching'),
    path('api/dispatch/reserve/', ReserveInventoryAPIView.as_view(), name='reserve-inventory'),
]