from django.urls import path, include
from core import views

urlpatterns = [
    path("setup/", views.setup,name="setup"),
    path("access/", views.get_access_code,name="access"),
    path("list/", views.item_list,name="ticks"),
]
