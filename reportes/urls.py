from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.ReportesDashboardView.as_view(), name='dashboard'),
    path('inventario/', views.ReporteInventarioView.as_view(), name='inventario'),
    path('inventario/excel/', views.ReporteInventarioExcelView.as_view(), name='inventario_excel'),
    path('inventario/pdf/', views.ReporteInventarioPDFView.as_view(), name='inventario_pdf'),
    path('api/equipos-por-ubicacion/', views.EquiposPorUbicacionAPI.as_view(), name='api_equipos_ubicacion'),
    path('api/equipos-por-estado/', views.EquiposPorEstadoAPI.as_view(), name='api_equipos_estado'),
    path('api/incidencias-por-mes/', views.IncidenciasPorMesAPI.as_view(), name='api_incidencias_mes'),
    path('api/incidencias-por-prioridad/', views.IncidenciasPorPrioridadAPI.as_view(), name='api_incidencias_prioridad'),
    path('api/equipos-mas-fallas/', views.EquiposMasFallasAPI.as_view(), name='api_equipos_fallas'),
    path('api/mantenimientos-por-periodo/', views.MantenimientosPorPeriodoAPI.as_view(), name='api_mantenimientos_periodo'),
]
