from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

# Importamos tus modelos y el serializador
from app_movil_escolar_api.models import Evento, Administradores, Maestros, Alumnos
from app_movil_escolar_api.serializers import EventoSerializer

class EventoViewSet(viewsets.ModelViewSet):
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated] 


    def get_queryset(self):
        user = self.request.user
        # Obtenemos todos los eventos ordenados por ID 
        queryset = Evento.objects.all().order_by('id')

        
        if user.is_superuser:
            return queryset

        
        if Administradores.objects.filter(user=user).exists():
            return queryset

        # CASO C: Si es Maestro
        # Regla: Ver eventos propios para "Profesores" O "Público en general"
        if Maestros.objects.filter(user=user).exists():
            return queryset.filter(
                Q(publico_objetivo__icontains='Profesores') | 
                Q(publico_objetivo__icontains='Público en general')
            )

        # CASO D: Si es Alumno
        # Regla: Ver eventos propios para "Estudiantes" O "Público en general"
        if Alumnos.objects.filter(user=user).exists():
            return queryset.filter(
                Q(publico_objetivo__icontains='Estudiantes') | 
                Q(publico_objetivo__icontains='Público en general')
            )

        # Si no tiene rol válido, no ve nada por seguridad
        return queryset.none()

    
    # Crear Evento (POST) - SOLO ADMINS
    def create(self, request, *args, **kwargs):
        if not self.es_admin(request.user):
             return Response(
                 {"error": "Acción denegada. Solo los administradores pueden registrar eventos."}, 
                 status=status.HTTP_403_FORBIDDEN
             )
        return super().create(request, *args, **kwargs)

    # Editar Evento (PUT/PATCH) - SOLO ADMINS
    def update(self, request, *args, **kwargs):
        if not self.es_admin(request.user):
             return Response(
                 {"error": "Acción denegada. No tienes permisos para editar eventos."}, 
                 status=status.HTTP_403_FORBIDDEN
             )
        return super().update(request, *args, **kwargs)

    # Eliminar Evento (DELETE) - SOLO ADMINS
    def destroy(self, request, *args, **kwargs):
        if not self.es_admin(request.user):
             return Response(
                 {"error": "Acción denegada. No tienes permisos para eliminar eventos."}, 
                 status=status.HTTP_403_FORBIDDEN
             )
        return super().destroy(request, *args, **kwargs)

    # Función auxiliar para verificar si es admin
    def es_admin(self, user):
        return user.is_superuser or Administradores.objects.filter(user=user).exists()