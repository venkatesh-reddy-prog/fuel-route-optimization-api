from django.urls import path
from .views import RouteAPIView, map_view

urlpatterns = [
    path("route/", RouteAPIView.as_view(), name="route"),
    path("map/", map_view, name="map"),
]