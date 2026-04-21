from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Administrador, Aula, Docente, Estudiante, Grupo, Inscripcion, Materia, Periodo, SolicitudDocente, TareaCurso

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
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)
    departamento = serializers.CharField(max_length=120, required=False, allow_blank=True)
    especializacion = serializers.CharField(max_length=160, required=False, allow_blank=True)
    tipo_contrato = serializers.CharField(max_length=80, required=False, allow_blank=True)
    fecha_contratacion = serializers.DateField(required=False, allow_null=True)
    horario_atencion = serializers.CharField(max_length=160, required=False, allow_blank=True)
    cubiculo = serializers.CharField(max_length=80, required=False, allow_blank=True)
    matricula = serializers.CharField(max_length=50, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)
    programa = serializers.CharField(max_length=150, required=False, allow_blank=True)
    semestre = serializers.CharField(max_length=50, required=False, allow_blank=True)
    fecha_inscripcion = serializers.DateField(required=False, allow_null=True)
    direccion = serializers.CharField(max_length=255, required=False, allow_blank=True)
    contacto_emergencia_nombre = serializers.CharField(max_length=150, required=False, allow_blank=True)
    contacto_emergencia_telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)

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
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)
    departamento = serializers.CharField(max_length=120, required=False, allow_blank=True)
    especializacion = serializers.CharField(max_length=160, required=False, allow_blank=True)
    tipo_contrato = serializers.CharField(max_length=80, required=False, allow_blank=True)
    fecha_contratacion = serializers.DateField(required=False, allow_null=True)
    horario_atencion = serializers.CharField(max_length=160, required=False, allow_blank=True)
    cubiculo = serializers.CharField(max_length=80, required=False, allow_blank=True)
    matricula = serializers.CharField(max_length=50, required=False, allow_blank=True)
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)
    programa = serializers.CharField(max_length=150, required=False, allow_blank=True)
    semestre = serializers.CharField(max_length=50, required=False, allow_blank=True)
    fecha_inscripcion = serializers.DateField(required=False, allow_null=True)
    direccion = serializers.CharField(max_length=255, required=False, allow_blank=True)
    contacto_emergencia_nombre = serializers.CharField(max_length=150, required=False, allow_blank=True)
    contacto_emergencia_telefono = serializers.CharField(max_length=30, required=False, allow_blank=True)

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
    grupos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Estudiante
        fields = "__all__"

    def get_grupos(self, obj):
        inscripciones = obj.inscripciones.select_related("grupo").all()

        return [
            {
                "id": inscripcion.grupo_id,
                "codigo": inscripcion.grupo.codigo,
                "materia": inscripcion.grupo.materia,
                "docente": inscripcion.grupo.docente,
                "aula": self._serialize_aula(inscripcion.grupo.aula),
                "semestre": inscripcion.grupo.semestre,
                "dia_semana": inscripcion.grupo.dias_semana,
                "hora_inicio": inscripcion.grupo.hora_inicio,
                "hora_fin": inscripcion.grupo.hora_fin,
                "cupo_max": inscripcion.grupo.cupo_max,
                "inscritos": inscripcion.grupo.inscritos,
                "fecha_inscripcion": inscripcion.fecha_inscripcion,
            }
            for inscripcion in inscripciones
        ]

    def _serialize_aula(self, aula):
        if aula is None:
            return None

        return {
            "id": aula.id,
            "edificio": aula.edificio,
            "numero": aula.numero,
            "capacidad": aula.capacidad,
            "estado": aula.estado,
        }


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
    dia_semana = serializers.ListField(
        child=serializers.CharField(max_length=20),
        source="dias_semana",
        required=False,
    )
    aula_id = serializers.PrimaryKeyRelatedField(
        queryset=Aula.objects.all(),
        source="aula",
        required=False,
        allow_null=True,
        write_only=True,
    )
    aula = serializers.SerializerMethodField(read_only=True)
    estudiante_ids = serializers.PrimaryKeyRelatedField(
        queryset=Estudiante.objects.select_related("usuario").all(),
        many=True,
        write_only=True,
        required=False,
        source="estudiantes_asignados",
    )
    estudiantes = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Grupo
        fields = (
            "id",
            "codigo",
            "materia",
            "docente",
            "aula_id",
            "aula",
            "semestre",
            "dia_semana",
            "hora_inicio",
            "hora_fin",
            "cupo_max",
            "inscritos",
            "estudiante_ids",
            "estudiantes",
        )
        read_only_fields = ("inscritos", "estudiantes", "aula")

    def validate(self, attrs):
        cupo_max = attrs.get("cupo_max")
        inscritos = attrs.get("inscritos")
        aula = attrs.get("aula")
        dia_semana = attrs.get("dias_semana")
        hora_inicio = attrs.get("hora_inicio")
        hora_fin = attrs.get("hora_fin")
        estudiantes_asignados = attrs.get("estudiantes_asignados")
        allowed_days = {"Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"}

        if self.instance is not None:
            if aula is None and "aula" not in attrs:
                aula = self.instance.aula
            if dia_semana is None:
                dia_semana = self.instance.dias_semana
            if hora_inicio is None:
                hora_inicio = self.instance.hora_inicio
            if hora_fin is None:
                hora_fin = self.instance.hora_fin

        if self.instance is not None:
            if cupo_max is None:
                cupo_max = self.instance.cupo_max
            if inscritos is None:
                inscritos = self.instance.inscritos

        if self.instance is not None and estudiantes_asignados is None:
            estudiantes_asignados = list(
                Estudiante.objects.filter(inscripciones__grupo=self.instance).distinct()
            )

        if dia_semana is not None:
            normalized_days = []

            for day in dia_semana:
                normalized_day = day.strip()

                if normalized_day not in allowed_days:
                    raise serializers.ValidationError({
                        "dia_semana": f"{normalized_day} no es un día válido para el horario.",
                    })

                if normalized_day not in normalized_days:
                    normalized_days.append(normalized_day)

            attrs["dias_semana"] = normalized_days
            dia_semana = normalized_days

        has_complete_schedule = bool(dia_semana) and hora_inicio is not None and hora_fin is not None
        has_partial_schedule = any([
            bool(dia_semana),
            hora_inicio is not None,
            hora_fin is not None,
        ]) and not has_complete_schedule

        if has_partial_schedule:
            raise serializers.ValidationError({
                "dia_semana": "Debes indicar dia, hora de inicio y hora de fin del grupo.",
            })

        if has_complete_schedule and hora_inicio >= hora_fin:
            raise serializers.ValidationError({
                "hora_fin": "La hora de fin debe ser posterior a la hora de inicio.",
            })

        if cupo_max is not None and cupo_max <= 0:
            raise serializers.ValidationError({"cupo_max": "El cupo maximo debe ser mayor a 0."})

        if aula is not None and cupo_max is not None and cupo_max > aula.capacidad:
            raise serializers.ValidationError({
                "aula_id": "El cupo maximo del grupo no puede exceder la capacidad del aula seleccionada.",
            })

        inscritos_calculados = len(estudiantes_asignados) if estudiantes_asignados is not None else inscritos

        if inscritos_calculados is not None and inscritos_calculados < 0:
            raise serializers.ValidationError({"inscritos": "El numero de inscritos no puede ser negativo."})

        if cupo_max is not None and inscritos_calculados is not None and inscritos_calculados > cupo_max:
            raise serializers.ValidationError({"estudiante_ids": "Los alumnos seleccionados exceden el cupo maximo del grupo."})

        if aula is not None and inscritos_calculados is not None and inscritos_calculados > aula.capacidad:
            raise serializers.ValidationError({
                "aula_id": "La cantidad de alumnos seleccionados excede la capacidad del aula seleccionada.",
            })

        attrs["inscritos"] = inscritos_calculados or 0

        return attrs

    def create(self, validated_data):
        estudiantes = validated_data.pop("estudiantes_asignados", [])
        grupo = super().create(validated_data)
        self._sync_enrollments(grupo, estudiantes)
        return grupo

    def update(self, instance, validated_data):
        estudiantes = validated_data.pop("estudiantes_asignados", None)
        grupo = super().update(instance, validated_data)

        if estudiantes is not None:
            self._sync_enrollments(grupo, estudiantes)
        else:
            grupo.sync_inscritos()

        return grupo

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["inscritos"] = instance.inscripciones.count()
        return data

    def get_estudiantes(self, obj):
        inscripciones = obj.inscripciones.select_related("estudiante__usuario").all()

        return [
            {
                "id": inscripcion.estudiante_id,
                "matricula": inscripcion.estudiante.matricula,
                "nombre": f"{inscripcion.estudiante.usuario.first_name} {inscripcion.estudiante.usuario.last_name}".strip() or inscripcion.estudiante.usuario.email,
                "email": inscripcion.estudiante.usuario.email,
                "programa": inscripcion.estudiante.programa,
                "semestre": inscripcion.estudiante.semestre,
                "fecha_inscripcion": inscripcion.fecha_inscripcion,
            }
            for inscripcion in inscripciones
        ]

    def get_aula(self, obj):
        if obj.aula is None:
            return None

        return {
            "id": obj.aula_id,
            "edificio": obj.aula.edificio,
            "numero": obj.aula.numero,
            "capacidad": obj.aula.capacidad,
            "estado": obj.aula.estado,
        }

    def _sync_enrollments(self, grupo, estudiantes):
        current_student_ids = set(grupo.inscripciones.values_list("estudiante_id", flat=True))
        next_student_ids = {estudiante.usuario_id for estudiante in estudiantes}

        to_remove = current_student_ids - next_student_ids
        to_add = next_student_ids - current_student_ids

        if to_remove:
            Inscripcion.objects.filter(grupo=grupo, estudiante_id__in=to_remove).delete()

        for student_id in to_add:
            Inscripcion.objects.create(grupo=grupo, estudiante_id=student_id)

        grupo.sync_inscritos()


class TareaCursoSerializer(serializers.ModelSerializer):
    grupo_id = serializers.PrimaryKeyRelatedField(queryset=Grupo.objects.all(), source="grupo", write_only=True)
    grupo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TareaCurso
        fields = (
            "id",
            "grupo_id",
            "grupo",
            "titulo",
            "descripcion",
            "fecha_entrega",
            "creation",
        )
        read_only_fields = ("id", "grupo", "creation")

    def get_grupo(self, obj):
        return {
            "id": obj.grupo_id,
            "codigo": obj.grupo.codigo,
            "materia": obj.grupo.materia,
            "semestre": obj.grupo.semestre,
        }

    def validate(self, attrs):
        titulo = attrs.get("titulo")
        descripcion = attrs.get("descripcion")

        if titulo is not None:
            attrs["titulo"] = titulo.strip()

        if descripcion is not None:
            attrs["descripcion"] = descripcion.strip()

        return attrs


class AulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aula
        fields = ("id", "edificio", "numero", "capacidad", "recursos", "estado")

    def validate(self, attrs):
        capacidad = attrs.get("capacidad")
        recursos = attrs.get("recursos")

        if capacidad is not None and capacidad <= 0:
            raise serializers.ValidationError({"capacidad": "La capacidad debe ser mayor a 0."})

        if recursos is not None and not isinstance(recursos, list):
            raise serializers.ValidationError({"recursos": "Los recursos deben enviarse como una lista."})

        return attrs


class SolicitudDocenteSerializer(serializers.ModelSerializer):
    docente = DocenteSerializer(read_only=True)
    admin_resuelve = AdministradorSerializer(read_only=True)

    class Meta:
        model = SolicitudDocente
        fields = (
            "id",
            "docente",
            "admin_resuelve",
            "tipo_solicitud",
            "aula",
            "motivo",
            "informacion_adicional",
            "estado",
            "fecha_solicitud",
            "fecha_resolucion",
        )
        read_only_fields = ("id", "docente", "admin_resuelve", "fecha_solicitud", "fecha_resolucion")

    def validate(self, attrs):
        tipo_solicitud = attrs.get("tipo_solicitud")
        aula = attrs.get("aula")
        motivo = attrs.get("motivo")
        informacion_adicional = attrs.get("informacion_adicional")
        estado = attrs.get("estado")

        if tipo_solicitud is not None:
            attrs["tipo_solicitud"] = tipo_solicitud.strip()

        if aula is not None:
            attrs["aula"] = aula.strip()

        if motivo is not None:
            attrs["motivo"] = motivo.strip()

        if informacion_adicional is not None:
            attrs["informacion_adicional"] = informacion_adicional.strip()

        if self.instance is None and estado is not None and estado != SolicitudDocente.Estado.PENDIENTE:
            raise serializers.ValidationError({"estado": "Las nuevas solicitudes se crean siempre como pendientes."})

        return attrs

