from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('id','first_name','last_name', 'email')

class AdminSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Administradores
        fields = '__all__'
        
class AlumnoSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Alumnos
        fields = "__all__"

class MaestroSerializer(serializers.ModelSerializer):
    user=UserSerializer(read_only=True)
    class Meta:
        model = Maestros
        fields = '__all__'

# --- SERIALIZADOR DE EVENTOS CON VALIDACIONES ---
class EventoSerializer(serializers.ModelSerializer):
    # Campo extra de solo lectura para mostrar el nombre completo en el frontend
    responsable_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Evento
        fields = '__all__'

    def get_responsable_nombre(self, obj):
        if obj.responsable:
            return f"{obj.responsable.first_name} {obj.responsable.last_name}"
        return "Sin responsable"

    # --- VALIDACIONES (Para evitar error 500) ---
    def validate(self, data):
        # 1. Validar Fecha (No anterior a hoy)
        fecha = data.get('fecha')
        
        # Si estamos creando (no hay instancia) o si estamos editando y cambiaron la fecha
        if fecha:
             if fecha < datetime.date.today():
                raise serializers.ValidationError({"fecha": "La fecha no puede ser anterior al día de hoy."})

        # 2. Validar Horas
        hora_inicio = data.get('hora_inicio')
        hora_fin = data.get('hora_fin')
        
        # Recuperamos los valores actuales si es una edición y no vienen en la petición
        if self.instance:
            if not hora_inicio:
                hora_inicio = self.instance.hora_inicio
            if not hora_fin:
                hora_fin = self.instance.hora_fin

        # Validamos la lógica de horario
        if hora_inicio and hora_fin:
            if hora_inicio >= hora_fin:
                raise serializers.ValidationError({"hora_fin": "La hora de fin debe ser posterior a la hora de inicio."})

        return data