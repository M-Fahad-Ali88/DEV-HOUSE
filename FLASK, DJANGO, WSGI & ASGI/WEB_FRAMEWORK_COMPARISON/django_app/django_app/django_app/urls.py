from django.contrib import admin
from django.urls import path
from api import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/hello", views.hello),
    path("api/users", views.get_users),
    path("api/users/create", views.create_user),
]