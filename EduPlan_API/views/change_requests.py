from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response

from EduPlan_API.models import SolicitudDocente, Usuario
from EduPlan_API.serializers import SolicitudDocenteSerializer


class SolicitudesView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user

        if user.tipo_usuario == Usuario.TipoUsuario.ADMIN:
            solicitudes = SolicitudDocente.objects.select_related(
                "docente__usuario",
                "admin_resuelve__usuario",
            )
        elif user.tipo_usuario == Usuario.TipoUsuario.DOCENTE:
            docente = getattr(user, "docente", None)
            if not docente:
                return Response({"message": "Docente no encontrado."}, status=status.HTTP_404_NOT_FOUND)
            solicitudes = SolicitudDocente.objects.select_related(
                "docente__usuario",
                "admin_resuelve__usuario",
            ).filter(docente=docente)
        else:
            return Response({"message": "No tienes permisos para consultar solicitudes."}, status=status.HTTP_403_FORBIDDEN)

        return Response(SolicitudDocenteSerializer(solicitudes, many=True).data)

    def post(self, request, *args, **kwargs):
        user = request.user

        if user.tipo_usuario != Usuario.TipoUsuario.DOCENTE:
            return Response({"message": "Solo los docentes pueden crear solicitudes."}, status=status.HTTP_403_FORBIDDEN)

        docente = getattr(user, "docente", None)
        if not docente:
            return Response({"message": "Docente no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SolicitudDocenteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save(docente=docente, estado=SolicitudDocente.Estado.PENDIENTE)
        return Response(SolicitudDocenteSerializer(solicitud).data, status=status.HTTP_201_CREATED)


class SolicitudDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return SolicitudDocente.objects.select_related(
            "docente__usuario",
            "admin_resuelve__usuario",
        ).filter(pk=pk).first()

    def patch(self, request, pk, *args, **kwargs):
        user = request.user
        solicitud = self.get_object(pk)

        if not solicitud:
            return Response({"message": "Solicitud no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if user.tipo_usuario != Usuario.TipoUsuario.ADMIN:
            return Response({"message": "Solo el administrador puede actualizar solicitudes."}, status=status.HTTP_403_FORBIDDEN)

        serializer = SolicitudDocenteSerializer(solicitud, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_request = serializer.save(
            admin_resuelve=getattr(user, "administrador", None),
            fecha_resolucion=timezone.now() if serializer.validated_data.get("estado") in {
                SolicitudDocente.Estado.APROBADA,
                SolicitudDocente.Estado.RECHAZADA,
            } else solicitud.fecha_resolucion,
        )
        return Response(SolicitudDocenteSerializer(updated_request).data)

    def delete(self, request, pk, *args, **kwargs):
        user = request.user
        solicitud = self.get_object(pk)

        if not solicitud:
            return Response({"message": "Solicitud no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if user.tipo_usuario == Usuario.TipoUsuario.ADMIN:
            solicitud.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        if user.tipo_usuario == Usuario.TipoUsuario.DOCENTE and getattr(user, "docente", None) == solicitud.docente:
            if solicitud.estado != SolicitudDocente.Estado.PENDIENTE:
                return Response({"message": "Solo puedes eliminar solicitudes pendientes."}, status=status.HTTP_400_BAD_REQUEST)

            solicitud.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"message": "No tienes permisos para eliminar esta solicitud."}, status=status.HTTP_403_FORBIDDEN)