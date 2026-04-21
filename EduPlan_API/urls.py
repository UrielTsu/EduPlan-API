from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views.auth import CustomAuthToken, Logout
from .views.bootstrap import VersionView
from .views.classrooms import AulaDetailView, AulasView
from .views.change_requests import SolicitudDetailView, SolicitudesView
from .views.groups import GrupoDetailView, GruposView
from .views.periods import PeriodoDetailView, PeriodosView
from .views.subjects import MateriaDetailView, MateriasView
from .views.tasks import TareaCursoDetailView, TareasCursoView
from .views.users import (
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
    path("api/periodos/", PeriodosView.as_view(), name="api-periodos"),
    path("api/periodos/<int:pk>/", PeriodoDetailView.as_view(), name="api-periodo-detail"),
    path("api/materias/", MateriasView.as_view(), name="api-materias"),
    path("api/materias/<int:pk>/", MateriaDetailView.as_view(), name="api-materia-detail"),
    path("api/grupos/", GruposView.as_view(), name="api-grupos"),
    path("api/grupos/<int:pk>/", GrupoDetailView.as_view(), name="api-grupo-detail"),
    path("api/aulas/", AulasView.as_view(), name="api-aulas"),
    path("api/aulas/<int:pk>/", AulaDetailView.as_view(), name="api-aula-detail"),
    path("api/solicitudes/", SolicitudesView.as_view(), name="api-solicitudes"),
    path("api/solicitudes/<int:pk>/", SolicitudDetailView.as_view(), name="api-solicitud-detail"),
    path("api/tareas/", TareasCursoView.as_view(), name="api-tareas"),
    path("api/tareas/<int:pk>/", TareaCursoDetailView.as_view(), name="api-tarea-detail"),
    path("api/docentes/", DocentesView.as_view(), name="api-docentes"),
    path("api/docentes/<int:pk>/", DocenteDetailView.as_view(), name="api-docente-detail"),
    path("api/estudiantes/", EstudiantesView.as_view(), name="api-estudiantes"),
    path("api/estudiantes/<int:pk>/", EstudianteDetailView.as_view(), name="api-estudiante-detail"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
