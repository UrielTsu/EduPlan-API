from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from EduPlan_API.models import Administrador, Docente, Estudiante
from EduPlan_API.serializers import (
    AdministradorSerializer,
    DocenteSerializer,
    EstudianteSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserSerializer,
)
from rest_framework import generics, permissions, status
from rest_framework.response import Response

User = get_user_model()


def _format_validation_error(exc):
    if hasattr(exc, "messages") and exc.messages:
        return exc.messages
    return [str(exc)]


def _create_role_user(validated_data, tipo_usuario):
    first_name = validated_data["first_name"]
    last_name = validated_data.get("last_name", "")
    email = validated_data["email"]
    password = validated_data["password"]
    is_active = validated_data.get("is_active", True)
    numero_empleado = validated_data.get("numero_empleado", "").strip()
    matricula = validated_data.get("matricula", "").strip()

    if User.objects.filter(email=email).exists():
        return None, Response({"message": f"El correo {email} ya existe."}, status=status.HTTP_400_BAD_REQUEST)

    if tipo_usuario == User.TipoUsuario.ADMIN and Administrador.objects.exists():
        return None, Response(
            {"message": "Solo puede existir un administrador en el sistema."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if tipo_usuario == User.TipoUsuario.DOCENTE and not numero_empleado:
        return None, Response(
            {"message": "El numero de empleado es obligatorio para docentes."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if tipo_usuario == User.TipoUsuario.ESTUDIANTE and not matricula:
        return None, Response(
            {"message": "La matricula es obligatoria para estudiantes."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = User(
        email=email,
        first_name=first_name,
        last_name=last_name,
        tipo_usuario=tipo_usuario,
        is_active=is_active,
        is_staff=tipo_usuario == User.TipoUsuario.ADMIN,
        is_superuser=tipo_usuario == User.TipoUsuario.ADMIN,
    )
    try:
        validate_password(password, user)
    except DjangoValidationError as exc:
        return None, Response({"password": _format_validation_error(exc)}, status=status.HTTP_400_BAD_REQUEST)
    user.set_password(password)
    user.save()

    if tipo_usuario == User.TipoUsuario.ADMIN:
        Administrador.objects.create(usuario=user)
        return Administrador.objects.get(usuario=user), None

    if tipo_usuario == User.TipoUsuario.DOCENTE:
        return Docente.objects.create(usuario=user, numero_empleado=numero_empleado), None

    return Estudiante.objects.create(usuario=user, matricula=matricula), None


def _update_role_user(user, relation, validated_data, tipo_usuario):
    email = validated_data.get("email")
    if email and User.objects.exclude(pk=user.pk).filter(email=email).exists():
        return Response({"message": f"El correo {email} ya existe."}, status=status.HTTP_400_BAD_REQUEST)

    if email is not None:
        user.email = email
    if "first_name" in validated_data:
        user.first_name = validated_data["first_name"]
    if "last_name" in validated_data:
        user.last_name = validated_data["last_name"]
    if "is_active" in validated_data:
        user.is_active = validated_data["is_active"]
    user.tipo_usuario = tipo_usuario

    password = validated_data.get("password", "")
    if password:
        try:
            validate_password(password, user)
        except DjangoValidationError as exc:
            return Response({"password": _format_validation_error(exc)}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(password)

    user.save()

    if tipo_usuario == User.TipoUsuario.DOCENTE and "numero_empleado" in validated_data:
        numero_empleado = validated_data["numero_empleado"].strip()
        if Docente.objects.exclude(pk=relation.pk).filter(numero_empleado=numero_empleado).exists():
            return Response({"message": f"El numero de empleado {numero_empleado} ya existe."}, status=status.HTTP_400_BAD_REQUEST)
        relation.numero_empleado = numero_empleado
        relation.save()

    if tipo_usuario == User.TipoUsuario.ESTUDIANTE and "matricula" in validated_data:
        matricula = validated_data["matricula"].strip()
        if Estudiante.objects.exclude(pk=relation.pk).filter(matricula=matricula).exists():
            return Response({"message": f"La matricula {matricula} ya existe."}, status=status.HTTP_400_BAD_REQUEST)
        relation.matricula = matricula
        relation.save()

    return None

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
        tipo_usuario = serializer.validated_data["tipo_usuario"]
        relation, error_response = _create_role_user(serializer.validated_data, tipo_usuario)
        if error_response:
            return error_response

        if tipo_usuario == User.TipoUsuario.ADMIN:
            return Response({"administrador": AdministradorSerializer(relation).data}, status=status.HTTP_201_CREATED)
        if tipo_usuario == User.TipoUsuario.DOCENTE:
            return Response(DocenteSerializer(relation).data, status=status.HTTP_201_CREATED)
        return Response(EstudianteSerializer(relation).data, status=status.HTTP_201_CREATED)


class DocentesView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        docentes = Docente.objects.select_related("usuario").order_by("usuario__first_name", "usuario__last_name")
        return Response(DocenteSerializer(docentes, many=True).data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload["tipo_usuario"] = User.TipoUsuario.DOCENTE
        serializer = UserCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        docente, error_response = _create_role_user(serializer.validated_data, User.TipoUsuario.DOCENTE)
        if error_response:
            return error_response
        return Response(DocenteSerializer(docente).data, status=status.HTTP_201_CREATED)


class DocenteDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return Docente.objects.select_related("usuario").filter(pk=pk).first()

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        docente = self.get_object(pk)
        if not docente:
            return Response({"message": "Docente no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(data=request.data, partial=True, context={"tipo_usuario": User.TipoUsuario.DOCENTE})
        serializer.is_valid(raise_exception=True)
        error_response = _update_role_user(docente.usuario, docente, serializer.validated_data, User.TipoUsuario.DOCENTE)
        if error_response:
            return error_response
        return Response(DocenteSerializer(docente).data)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        docente = self.get_object(pk)
        if not docente:
            return Response({"message": "Docente no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        docente.usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EstudiantesView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        estudiantes = Estudiante.objects.select_related("usuario").order_by("usuario__first_name", "usuario__last_name")
        return Response(EstudianteSerializer(estudiantes, many=True).data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        payload = request.data.copy()
        payload["tipo_usuario"] = User.TipoUsuario.ESTUDIANTE
        serializer = UserCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        estudiante, error_response = _create_role_user(serializer.validated_data, User.TipoUsuario.ESTUDIANTE)
        if error_response:
            return error_response
        return Response(EstudianteSerializer(estudiante).data, status=status.HTTP_201_CREATED)


class EstudianteDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return Estudiante.objects.select_related("usuario").filter(pk=pk).first()

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        estudiante = self.get_object(pk)
        if not estudiante:
            return Response({"message": "Estudiante no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserUpdateSerializer(data=request.data, partial=True, context={"tipo_usuario": User.TipoUsuario.ESTUDIANTE})
        serializer.is_valid(raise_exception=True)
        error_response = _update_role_user(estudiante.usuario, estudiante, serializer.validated_data, User.TipoUsuario.ESTUDIANTE)
        if error_response:
            return error_response
        return Response(EstudianteSerializer(estudiante).data)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        estudiante = self.get_object(pk)
        if not estudiante:
            return Response({"message": "Estudiante no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        estudiante.usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
