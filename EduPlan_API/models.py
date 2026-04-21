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
    telefono = models.CharField(max_length=30, blank=True)
    departamento = models.CharField(max_length=120, blank=True)
    especializacion = models.CharField(max_length=160, blank=True)
    tipo_contrato = models.CharField(max_length=80, blank=True)
    fecha_contratacion = models.DateField(null=True, blank=True)
    horario_atencion = models.CharField(max_length=160, blank=True)
    cubiculo = models.CharField(max_length=80, blank=True)
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


class Inscripcion(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="inscripciones")
    grupo = models.ForeignKey("Grupo", on_delete=models.CASCADE, related_name="inscripciones")
    fecha_inscripcion = models.DateField(auto_now_add=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_inscripcion", "-id"]
        unique_together = ("estudiante", "grupo")

    def __str__(self):
        return f"{self.estudiante.usuario.email} -> {self.grupo.codigo}"


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
    aula = models.ForeignKey("Aula", on_delete=models.SET_NULL, related_name="grupos", null=True, blank=True)
    semestre = models.CharField(max_length=50)
    dias_semana = models.JSONField(default=list, blank=True)
    hora_inicio = models.TimeField(null=True, blank=True)
    hora_fin = models.TimeField(null=True, blank=True)
    cupo_max = models.PositiveIntegerField()
    inscritos = models.PositiveIntegerField(default=0)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["codigo", "id"]

    def __str__(self):
        return self.codigo

    def sync_inscritos(self):
        inscritos = self.inscripciones.count()

        if self.inscritos != inscritos:
            self.inscritos = inscritos
            self.save(update_fields=["inscritos", "update"])


class TareaCurso(models.Model):
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="tareas")
    titulo = models.CharField(max_length=160)
    descripcion = models.TextField(blank=True)
    fecha_entrega = models.DateField()
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha_entrega", "id"]

    def __str__(self):
        return f"{self.grupo.codigo} - {self.titulo}"


class Aula(models.Model):
    class Estado(models.TextChoices):
        DISPONIBLE = "Disponible", "Disponible"
        OCUPADO = "Ocupado", "Ocupado"
        FUERA_DE_SERVICIO = "Fuera de servicio", "Fuera de servicio"

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


class SolicitudDocente(models.Model):
    class Tipo(models.TextChoices):
        CAMBIO_AULA = "Cambio de Aula", "Cambio de Aula"
        REPORTE_FALLA = "Reporte de Falla Tecnica", "Reporte de Falla Tecnica"
        SOLICITUD_MATERIAL = "Solicitud de Material", "Solicitud de Material"
        AJUSTE_HORARIO = "Ajuste de Horario", "Ajuste de Horario"

    class Estado(models.TextChoices):
        PENDIENTE = "Pendiente", "Pendiente"
        APROBADA = "Aprobada", "Aprobada"
        RECHAZADA = "Rechazada", "Rechazada"

    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name="solicitudes")
    admin_resuelve = models.ForeignKey(
        Administrador,
        on_delete=models.SET_NULL,
        related_name="solicitudes_resueltas",
        null=True,
        blank=True,
    )
    tipo_solicitud = models.CharField(max_length=60, choices=Tipo.choices)
    aula = models.CharField(max_length=120)
    motivo = models.CharField(max_length=200)
    informacion_adicional = models.TextField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.PENDIENTE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    creation = models.DateTimeField(auto_now_add=True)
    update = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha_solicitud", "-id"]

    def __str__(self):
        return f"{self.tipo_solicitud} - {self.docente.usuario.email}"

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

