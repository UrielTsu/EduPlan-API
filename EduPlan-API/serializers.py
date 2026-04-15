import re

from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Administrador, Docente, Estudiante

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "first_name", "last_name", "email", "tipo_usuario", "is_active", "creation")

class UserCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, write_only=True)
    is_active = serializers.BooleanField(required=False, default=True)
    tipo_usuario = serializers.ChoiceField(choices=User.TipoUsuario.choices)
    numero_empleado = serializers.CharField(max_length=50, required=False, allow_blank=True)
    matricula = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate(self, attrs):
        email = attrs["email"].strip().lower()
        tipo_usuario = attrs["tipo_usuario"]

        if tipo_usuario == User.TipoUsuario.DOCENTE:
            if not re.fullmatch(r"profesor([._-][a-z0-9]+)*@eduplan\.com", email):
                raise serializers.ValidationError({
                    "email": "El correo del docente debe seguir la estructura profesor@eduplan.com o profesor.algo@eduplan.com."
                })

        if tipo_usuario == User.TipoUsuario.ESTUDIANTE:
            if not re.fullmatch(r"alumno([._-][a-z0-9]+)*@eduplan\.com", email):
                raise serializers.ValidationError({
                    "email": "El correo del estudiante debe seguir la estructura alumno@eduplan.com o alumno.algo@eduplan.com."
                })

        attrs["email"] = email
        return attrs


class UserUpdateSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False)
    password = serializers.CharField(min_length=6, required=False, allow_blank=True, write_only=True)
    is_active = serializers.BooleanField(required=False)
    numero_empleado = serializers.CharField(max_length=50, required=False, allow_blank=True)
    matricula = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate(self, attrs):
        role = self.context.get("tipo_usuario")
        email = attrs.get("email")

        if email is not None:
            email = email.strip().lower()
            attrs["email"] = email

            if role == User.TipoUsuario.DOCENTE and not re.fullmatch(r"profesor([._-][a-z0-9]+)*@eduplan\.com", email):
                raise serializers.ValidationError({
                    "email": "El correo del docente debe seguir la estructura profesor@eduplan.com o profesor.algo@eduplan.com."
                })

            if role == User.TipoUsuario.ESTUDIANTE and not re.fullmatch(r"alumno([._-][a-z0-9]+)*@eduplan\.com", email):
                raise serializers.ValidationError({
                    "email": "El correo del estudiante debe seguir la estructura alumno@eduplan.com o alumno.algo@eduplan.com."
                })

        return attrs


class AdministradorSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = Administrador
        fields = "__all__"


class DocenteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = Docente
        fields = "__all__"


class EstudianteSerializer(serializers.ModelSerializer):
    usuario = UserSerializer(read_only=True)

    class Meta:
        model = Estudiante
        fields = "__all__"

