from rest_framework import generics, permissions, status
from rest_framework.response import Response

from EduPlan_API.models import Grupo, Usuario
from EduPlan_API.serializers import GrupoSerializer


class GruposView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        grupos = Grupo.objects.select_related("aula").prefetch_related(
            "inscripciones__estudiante__usuario"
        ).all()
        user = request.user

        if user.tipo_usuario == Usuario.TipoUsuario.DOCENTE:
            full_name = f"{user.first_name} {user.last_name}".strip()

            if not full_name:
                return Response([], status=status.HTTP_200_OK)

            grupos = grupos.filter(docente__iexact=full_name)

        return Response(GrupoSerializer(grupos, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = GrupoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        grupo = serializer.save()
        return Response(GrupoSerializer(grupo).data, status=status.HTTP_201_CREATED)


class GrupoDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return Grupo.objects.select_related("aula").prefetch_related("inscripciones__estudiante__usuario").filter(pk=pk).first()

    def patch(self, request, pk, *args, **kwargs):
        grupo = self.get_object(pk)
        if not grupo:
            return Response({"message": "Grupo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GrupoSerializer(grupo, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        grupo = self.get_object(pk)
        if not grupo:
            return Response({"message": "Grupo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        grupo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
