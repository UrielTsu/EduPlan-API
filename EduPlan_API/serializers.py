from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Administrador, Docente, Estudiante, Grupo, Materia, Periodo

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
        email = attrs.get("email")

        if email is not None:
            email = email.strip().lower()
            attrs["email"] = email

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


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ("id", "nombre", "fecha_inicio", "fecha_fin", "estado")

    def validate(self, attrs):
        fecha_inicio = attrs.get("fecha_inicio")
        fecha_fin = attrs.get("fecha_fin")

        if self.instance is not None:
            if fecha_inicio is None:
                fecha_inicio = self.instance.fecha_inicio
            if fecha_fin is None:
                fecha_fin = self.instance.fecha_fin

        if fecha_inicio and fecha_fin and fecha_inicio > fecha_fin:
            raise serializers.ValidationError({
                "fecha_fin": "La fecha de fin no puede ser menor que la fecha de inicio."
            })

        return attrs


class MateriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materia
        fields = ("id", "nombre", "codigo", "creditos", "area_academica")

    def validate(self, attrs):
        codigo = attrs.get("codigo")
        creditos = attrs.get("creditos")

        if codigo is not None:
            attrs["codigo"] = codigo.strip().upper()

        if creditos is not None and creditos <= 0:
            raise serializers.ValidationError({
                "creditos": "Los creditos deben ser mayores a 0."
            })

        return attrs


class GrupoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Grupo
        fields = ("id", "codigo", "materia", "docente", "semestre", "cupo_max", "inscritos")

    def validate(self, attrs):
        cupo_max = attrs.get("cupo_max")
        inscritos = attrs.get("inscritos")

        if self.instance is not None:
            if cupo_max is None:
                cupo_max = self.instance.cupo_max
            if inscritos is None:
                inscritos = self.instance.inscritos

        if cupo_max is not None and cupo_max <= 0:
            raise serializers.ValidationError({"cupo_max": "El cupo maximo debe ser mayor a 0."})

        if inscritos is not None and inscritos < 0:
            raise serializers.ValidationError({"inscritos": "El numero de inscritos no puede ser negativo."})

        if cupo_max is not None and inscritos is not None and inscritos > cupo_max:
            raise serializers.ValidationError({"inscritos": "Los inscritos no pueden exceder el cupo maximo."})

        return attrs

