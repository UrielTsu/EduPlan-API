from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from EduPlan_API.views.auth import CustomAuthToken, Logout
from EduPlan_API.views.bootstrap import VersionView
from EduPlan_API.views.users import (
	DocenteDetailView,
	DocentesView,
	EstudianteDetailView,
	EstudiantesView,
	Userme,
	UsersView,
)


urlpatterns = [
	path("admin/", admin.site.urls),
	path("api-auth/", include("rest_framework.urls")),
	path("api/version/", VersionView.as_view(), name="api-version"),
	path("api/auth/login/", CustomAuthToken.as_view(), name="api-login"),
	path("api/auth/logout/", Logout.as_view(), name="api-logout"),
	path("api/users/", UsersView.as_view(), name="api-users"),
	path("api/users/me/", Userme.as_view(), name="api-users-me"),
	path("api/docentes/", DocentesView.as_view(), name="api-docentes"),
	path("api/docentes/<int:pk>/", DocenteDetailView.as_view(), name="api-docente-detail"),
	path("api/estudiantes/", EstudiantesView.as_view(), name="api-estudiantes"),
	path("api/estudiantes/<int:pk>/", EstudianteDetailView.as_view(), name="api-estudiante-detail"),
]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)