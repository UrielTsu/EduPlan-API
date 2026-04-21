from rest_framework import generics, permissions, status
from rest_framework.response import Response

from EduPlan_API.models import Periodo
from EduPlan_API.serializers import PeriodoSerializer


class PeriodosView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        periodos = Periodo.objects.all()
        return Response(PeriodoSerializer(periodos, many=True).data)

    def post(self, request, *args, **kwargs):
        serializer = PeriodoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        periodo = serializer.save()
        return Response(PeriodoSerializer(periodo).data, status=status.HTTP_201_CREATED)


class PeriodoDetailView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, pk):
        return Periodo.objects.filter(pk=pk).first()

    def patch(self, request, pk, *args, **kwargs):
        periodo = self.get_object(pk)
        if not periodo:
            return Response({"message": "Periodo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PeriodoSerializer(periodo, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk, *args, **kwargs):
        periodo = self.get_object(pk)
        if not periodo:
            return Response({"message": "Periodo no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        periodo.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
