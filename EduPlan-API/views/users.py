from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from EduPlan_API.models import Administrador, Docente, Estudiante
from EduPlan_API.serializers import (
    AdministradorSerializer,
    DocenteSerializer,
    EstudianteSerializer,
    UserCreateSerializer,
    UserSerializer,
)
from rest_framework import generics, permissions, status
from rest_framework.response import Response

User = get_user_model()

class Userme(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class UsersView(generics.CreateAPIView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        first_name = serializer.validated_data["first_name"]
        last_name = serializer.validated_data.get("last_name", "")
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]
        tipo_usuario = serializer.validated_data["tipo_usuario"]
        numero_empleado = serializer.validated_data.get("numero_empleado", "").strip()
        matricula = serializer.validated_data.get("matricula", "").strip()

        if User.objects.filter(email=email).exists():
            return Response({"message": f"El correo {email} ya existe."}, status=status.HTTP_400_BAD_REQUEST)

        if tipo_usuario == User.TipoUsuario.ADMIN and Administrador.objects.exists():
            return Response(
                {"message": "Solo puede existir un administrador en el sistema."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tipo_usuario == User.TipoUsuario.DOCENTE and not numero_empleado:
            return Response(
                {"message": "El numero de empleado es obligatorio para docentes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if tipo_usuario == User.TipoUsuario.ESTUDIANTE and not matricula:
            return Response(
                {"message": "La matricula es obligatoria para estudiantes."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            tipo_usuario=tipo_usuario,
            is_active=True,
            is_staff=tipo_usuario == User.TipoUsuario.ADMIN,
            is_superuser=tipo_usuario == User.TipoUsuario.ADMIN,
        )
        validate_password(password, user)
        user.set_password(password)
        user.save()

        extra_payload = {}
        if tipo_usuario == User.TipoUsuario.ADMIN:
            Administrador.objects.create(usuario=user)
            extra_payload["administrador"] = AdministradorSerializer(user.administrador).data
        elif tipo_usuario == User.TipoUsuario.DOCENTE:
            Docente.objects.create(usuario=user, numero_empleado=numero_empleado)
            extra_payload["docente"] = DocenteSerializer(user.docente).data
        elif tipo_usuario == User.TipoUsuario.ESTUDIANTE:
            Estudiante.objects.create(usuario=user, matricula=matricula)
            extra_payload["estudiante"] = EstudianteSerializer(user.estudiante).data

        response_payload = {"usuario": UserSerializer(user).data, **extra_payload}
        return Response(response_payload, status=status.HTTP_201_CREATED)
