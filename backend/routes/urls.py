from django.urls import path
from .views import add_destination, get_destinations, delete_destination, optimize_route

urlpatterns = [
    path("add_destination/", add_destination, name="add_destination"),
    path("get_destinations/", get_destinations, name="get_destinations"),
    path("delete_destination/<int:id>/", delete_destination, name="delete_destination"),
    path("optimize_route/", optimize_route, name="optimize_route"),
]
