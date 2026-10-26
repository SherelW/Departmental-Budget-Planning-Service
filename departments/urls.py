from django.urls import path

from . import views

urlpatterns = [
    path("", views.departments, name="departments"),
    path(
        "<int:department_id>/",
        views.department_detail,
        name="department_detail",
    ),
]
