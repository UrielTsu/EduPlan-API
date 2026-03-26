from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.auth import CustomAuthToken, Logout
from .views.bootstrap import VersionView
from .views.users import Userme, UsersView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls")),
    path("api/version/", VersionView.as_view(), name="api-version"),
    path("api/auth/login/", CustomAuthToken.as_view(), name="api-login"),
    path("api/auth/logout/", Logout.as_view(), name="api-logout"),
    path("api/users/", UsersView.as_view(), name="api-users"),
    path("api/users/me/", Userme.as_view(), name="api-users-me"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
