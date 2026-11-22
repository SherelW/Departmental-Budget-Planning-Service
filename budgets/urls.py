from django.urls import path

from . import views

app_name = "budgets"

urlpatterns = [
    path("", views.budgets, name="list"),
    path("search/", views.budget_search, name="search"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:budget_id>/", views.budget_detail, name="detail"),
]
