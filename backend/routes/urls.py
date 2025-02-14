from django.urls import path
from .views import add_destination

urlpatterns = [
    path("add_destination/", add_destination, name="add_destination"),
]
