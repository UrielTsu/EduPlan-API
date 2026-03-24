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
    tipo_usuario = serializers.ChoiceField(choices=User.TipoUsuario.choices)
    numero_empleado = serializers.CharField(max_length=50, required=False, allow_blank=True)
    matricula = serializers.CharField(max_length=50, required=False, allow_blank=True)


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

