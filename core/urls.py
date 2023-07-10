from django.urls import path, include
from core import views

urlpatterns = [
    path("setup/", views.setup,name="setup"),
    path("access_code/", views.get_access_code,name="access_code"),
]
