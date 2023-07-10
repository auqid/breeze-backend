from django.urls import path, include
from core import views

urlpatterns = [
    path("test/", views.test,name="test"),
    path("access_code/", views.get_access_code,name="access_code"),
]
