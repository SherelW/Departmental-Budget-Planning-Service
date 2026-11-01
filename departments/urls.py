from django.urls import path

from . import views

app_name = "departments"

urlpatterns = [
    path("", views.departments, name="list"),
    path("<int:department_id>/", views.department_detail, name="detail"),
]
