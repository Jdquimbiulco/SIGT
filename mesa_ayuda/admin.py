from django.contrib import admin
from .models import Incidencia, Comentario


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ('pk', 'titulo', 'nombre_reportero', 'prioridad', 'estado', 'equipo', 'tecnico_asignado', 'fecha_creacion')
    list_filter = ('prioridad', 'estado', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion', 'equipo__marca', 'equipo__modelo', 'tecnico_asignado__username', 'creado_por__username')
    list_select_related = ('equipo', 'tecnico_asignado', 'creado_por')
    readonly_fields = ('fecha_creacion', 'fecha_resolucion')


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('incidencia', 'autor', 'fecha', 'texto')
    list_filter = ('fecha', 'autor')
    search_fields = ('texto', 'incidencia__titulo', 'autor__username')
    list_select_related = ('incidencia', 'autor')