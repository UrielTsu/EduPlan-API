from rest_framework import generics, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):
    # Maneja el POST de login: autentica al usuario con email/contraseña y retorna token
    # Si el usuario está activo, crea o recupera su token de autenticación
    # Si no está activo, retorna error 403 Forbidden
    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        # Convierte el email a username porque Django requiere el campo "username"
        if "email" in data and "username" not in data:
            data["username"] = data["email"]

        # Valida las credenciales usando el serializer de autenticación
        serializer = self.serializer_class(data=data, context={"request": request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        # Si el usuario está activo, genera o recupera el token y retorna datos del usuario
        if user.is_active:
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "id": user.pk,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "token": token.key,  # Token único para autenticación en próximas solicitudes
                "role": user.tipo_usuario,  # Rol del usuario (admin, docente, estudiante)
                "roles": [user.tipo_usuario],
            })
        # Si el usuario no está activo, rechaza la autenticación
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class Logout(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        if user.is_active:
            token = Token.objects.get(user=user)
            token.delete()

            return Response({"logout": True})

        return Response({"logout": False})
