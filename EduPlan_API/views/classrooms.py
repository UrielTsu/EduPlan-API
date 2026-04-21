from rest_framework import generics, permissions, status
from rest_framework.response import Response

from EduPlan_API.models import Aula
from EduPlan_API.serializers import AulaSerializer


class AulasView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        aulas = Aula.objects.all()
        return Response(AulaSerializer(aulas, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = AulaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        aula = serializer.save()
        return Response(AulaSerializer(aula).data, status=status.HTTP_201_CREATED)


class AulaDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return Aula.objects.filter(pk=pk).first()

    def patch(self, request, pk, *args, **kwargs):
        aula = self.get_object(pk)
        if not aula:
            return Response({"message": "Aula no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AulaSerializer(aula, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        aula = self.get_object(pk)
        if not aula:
            return Response({"message": "Aula no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        aula.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
