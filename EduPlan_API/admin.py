from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Administrador, Docente, Estudiante, Inscripcion, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    ordering = ("email",)
    list_display = ("id", "email", "first_name", "last_name", "tipo_usuario", "is_active", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informacion personal", {"fields": ("first_name", "last_name", "tipo_usuario")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas", {"fields": ("last_login", "creation", "update")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "first_name", "last_name", "tipo_usuario", "password1", "password2"),
            },
        ),
    )


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "creation", "update")
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name")


@admin.register(Docente)
class DocenteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "numero_empleado", "creation", "update")
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name", "numero_empleado")


@admin.register(Estudiante)
class EstudianteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "matricula", "creation", "update")
    search_fields = ("usuario__email", "usuario__first_name", "usuario__last_name", "matricula")


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "grupo", "fecha_inscripcion", "creation")
    search_fields = ("estudiante__usuario__email", "estudiante__matricula", "grupo__codigo", "grupo__materia")

