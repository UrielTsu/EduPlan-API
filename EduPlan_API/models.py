from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from rest_framework.authentication import TokenAuthentication


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("El correo es obligatorio.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("tipo_usuario", Usuario.TipoUsuario.ADMIN)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    class TipoUsuario(models.TextChoices):
        ADMIN = "admin", "Administrador"
        DOCENTE = "docente", "Docente"
        ESTUDIANTE = "estudiante", "Estudiante"

    username = None
    email = models.EmailField(unique=True)
    tipo_usuario = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.ESTUDIANTE,
    )
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UsuarioManager()

    def __str__(self):
        return self.email


class Administrador(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="administrador",
        primary_key=True,
    )
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and Administrador.objects.exists():
            raise ValidationError("Solo puede existir un administrador.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Administrador: {self.usuario.email}"


class Docente(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="docente",
        primary_key=True,
    )
    numero_empleado = models.CharField(max_length=50, unique=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Docente: {self.usuario.email}"


class Estudiante(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="estudiante",
        primary_key=True,
    )
    matricula = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=30, blank=True)
    programa = models.CharField(max_length=150, blank=True)
    semestre = models.CharField(max_length=50, blank=True)
    fecha_inscripcion = models.DateField(null=True, blank=True)
    direccion = models.CharField(max_length=255, blank=True)
    contacto_emergencia_nombre = models.CharField(max_length=150, blank=True)
    contacto_emergencia_telefono = models.CharField(max_length=30, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Estudiante: {self.usuario.email}"


class Periodo(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "Activo", "Activo"
        FINALIZADO = "Finalizado", "Finalizado"

    nombre = models.CharField(max_length=120, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_inicio", "-id"]

    def __str__(self):
        return self.nombre


class Materia(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=20, unique=True)
    creditos = models.PositiveIntegerField()
    area_academica = models.CharField(max_length=120)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre", "id"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Grupo(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    materia = models.CharField(max_length=150)
    docente = models.CharField(max_length=150, blank=True)
    semestre = models.CharField(max_length=50)
    cupo_max = models.PositiveIntegerField()
    inscritos = models.PositiveIntegerField(default=0)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["codigo", "id"]

    def __str__(self):
        return self.codigo


class Aula(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "Disponible", "Disponible"
        EN_USO = "En uso", "En uso"

    edificio = models.CharField(max_length=100)
    numero = models.CharField(max_length=50)
    capacidad = models.PositiveIntegerField()
    recursos = models.JSONField(default=list, blank=True)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.DISPONIBLE)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["edificio", "numero", "id"]
        unique_together = ("edificio", "numero")

    def __str__(self):
        return f"{self.edificio} - {self.numero}"

class BearerTokenAuthentication(TokenAuthentication):
    keyword = "Bearer"


@receiver(post_migrate)
def create_default_admin(sender, **kwargs):
    if sender.name != "EduPlan_API":
        return

    admin_email = getattr(settings, "DEFAULT_ADMIN_EMAIL", "admin@eduplan.com")
    admin_password = getattr(settings, "DEFAULT_ADMIN_PASSWORD", "admin123")

    user, created = Usuario.objects.get_or_create(
        email=admin_email,
        defaults={
            "first_name": "Admin",
            "last_name": "EduPlan",
            "tipo_usuario": Usuario.TipoUsuario.ADMIN,
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
        },
    )

    updated_fields = []
    if created:
        user.set_password(admin_password)
        updated_fields.append("password")

    if user.tipo_usuario != Usuario.TipoUsuario.ADMIN:
        user.tipo_usuario = Usuario.TipoUsuario.ADMIN
        updated_fields.append("tipo_usuario")
    if not user.is_active:
        user.is_active = True
        updated_fields.append("is_active")
    if not user.is_staff:
        user.is_staff = True
        updated_fields.append("is_staff")
    if not user.is_superuser:
        user.is_superuser = True
        updated_fields.append("is_superuser")

    if updated_fields:
        user.save(update_fields=updated_fields)

    Administrador.objects.get_or_create(usuario=user)

