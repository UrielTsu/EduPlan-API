from rest_framework import generics, permissions, status
from rest_framework.response import Response

from EduPlan_API.models import Materia
from EduPlan_API.serializers import MateriaSerializer


class MateriasView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        materias = Materia.objects.all()
        return Response(MateriaSerializer(materias, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = MateriaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        materia = serializer.save()
        return Response(MateriaSerializer(materia).data, status=status.HTTP_201_CREATED)


class MateriaDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return Materia.objects.filter(pk=pk).first()

    def patch(self, request, pk, *args, **kwargs):
        materia = self.get_object(pk)
        if not materia:
            return Response({"message": "Materia no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MateriaSerializer(materia, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        materia = self.get_object(pk)
        if not materia:
            return Response({"message": "Materia no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        materia.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
