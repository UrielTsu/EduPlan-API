from rest_framework import generics, permissions, status
from rest_framework.response import Response

from EduPlan_API.models import Grupo, TareaCurso, Usuario
from EduPlan_API.serializers import TareaCursoSerializer


def _normalize_name(value: str | None) -> str:
    return " ".join((value or "").strip().lower().split())


def _user_can_manage_group(user, grupo: Grupo) -> bool:
    if user.tipo_usuario == Usuario.TipoUsuario.ADMIN:
        return True

    if user.tipo_usuario != Usuario.TipoUsuario.DOCENTE:
        return False

    teacher_name = _normalize_name(f"{user.first_name} {user.last_name}")
    group_teacher = _normalize_name(grupo.docente)
    return bool(teacher_name) and teacher_name == group_teacher


class TareasCursoView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = TareaCurso.objects.select_related("grupo").all()
        user = self.request.user

        if user.tipo_usuario == Usuario.TipoUsuario.ADMIN:
            return queryset

        if user.tipo_usuario == Usuario.TipoUsuario.DOCENTE:
            teacher_name = _normalize_name(f"{user.first_name} {user.last_name}")
            if not teacher_name:
                return queryset.none()
            return queryset.filter(grupo__docente__iexact=f"{user.first_name} {user.last_name}".strip())

        if user.tipo_usuario == Usuario.TipoUsuario.ESTUDIANTE:
            return queryset.filter(grupo__inscripciones__estudiante_id=user.id).distinct()

        return queryset.none()

    def get(self, request, *args, **kwargs):
        tareas = self.get_queryset()
        grupo_id = request.query_params.get("grupo_id")

        if grupo_id:
            tareas = tareas.filter(grupo_id=grupo_id)

        return Response(TareaCursoSerializer(tareas, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = TareaCursoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grupo = serializer.validated_data["grupo"]

        if not _user_can_manage_group(request.user, grupo):
            return Response({"message": "No tienes permisos para crear tareas en este curso."}, status=status.HTTP_403_FORBIDDEN)

        tarea = serializer.save()
        return Response(TareaCursoSerializer(tarea).data, status=status.HTTP_201_CREATED)


class TareaCursoDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return TareaCurso.objects.select_related("grupo").filter(pk=pk).first()

    def patch(self, request, pk, *args, **kwargs):
        tarea = self.get_object(pk)
        if not tarea:
            return Response({"message": "Tarea no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if not _user_can_manage_group(request.user, tarea.grupo):
            return Response({"message": "No tienes permisos para editar esta tarea."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TareaCursoSerializer(tarea, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        grupo = serializer.validated_data.get("grupo", tarea.grupo)
        if not _user_can_manage_group(request.user, grupo):
            return Response({"message": "No tienes permisos para mover la tarea a ese curso."}, status=status.HTTP_403_FORBIDDEN)

        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        tarea = self.get_object(pk)
        if not tarea:
            return Response({"message": "Tarea no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if not _user_can_manage_group(request.user, tarea.grupo):
            return Response({"message": "No tienes permisos para eliminar esta tarea."}, status=status.HTTP_403_FORBIDDEN)

        tarea.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)