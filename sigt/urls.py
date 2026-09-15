from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta

from mesa_ayuda.views import ReportarIncidenciaView, ReporteExitosoView


@login_required
def dashboard(request):
    from inventario.models import Equipo
    from mesa_ayuda.models import Incidencia
    from mantenimiento.models import Mantenimiento

    hoy = timezone.now().date()

    total_equipos = Equipo.objects.count()
    equipos_activos = Equipo.objects.filter(estado='activo').count()
    incidencias_abiertas = Incidencia.objects.filter(estado__in=['abierta', 'en_proceso']).count()
    incidencias_urgentes = Incidencia.objects.filter(estado__in=['abierta', 'en_proceso'], prioridad='urgente').count()
    incidencias_resueltas_mes = Incidencia.objects.filter(
        estado__in=['resuelta', 'cerrada'],
        fecha_resolucion__month=hoy.month,
        fecha_resolucion__year=hoy.year
    ).count()
    mantenimientos_proximos = Mantenimiento.objects.filter(
        estado='programado',
        fecha_programada__range=[hoy, hoy + timedelta(days=7)]
    ).count()

    incidencias_recientes = Incidencia.objects.select_related('equipo', 'tecnico_asignado').order_by('-fecha_creacion')[:5]
    mantenimientos_lista = Mantenimiento.objects.select_related('equipo', 'tecnico').filter(
        estado='programado', fecha_programada__gte=hoy
    ).order_by('fecha_programada')[:5]

    context = {
        'total_equipos': total_equipos,
        'equipos_activos': equipos_activos,
        'incidencias_abiertas': incidencias_abiertas,
        'incidencias_urgentes': incidencias_urgentes,
        'incidencias_resueltas_mes': incidencias_resueltas_mes,
        'mantenimientos_proximos': mantenimientos_proximos,
        'incidencias_recientes': incidencias_recientes,
        'mantenimientos_lista': mantenimientos_lista,
    }
    return render(request, 'dashboard.html', context)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard, name='dashboard'),
    path('reportar/', ReportarIncidenciaView.as_view(), name='reportar'),
    path('reportar/ok/<int:pk>/', ReporteExitosoView.as_view(), name='reporte_exitoso'),
    path('inventario/', include('inventario.urls')),
    path('mesa-ayuda/', include('mesa_ayuda.urls')),
    path('mantenimiento/', include('mantenimiento.urls')),
    path('reportes/', include('reportes.urls')),
    path('usuarios/', include('usuarios.urls')),
]
