from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("departments/", include("departments.urls")),
    path("budgets/", include("budgets.urls")),
]

handler404 = "homepage.views.page_not_found"
