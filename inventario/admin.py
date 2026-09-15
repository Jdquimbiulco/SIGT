from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Equipo, HistorialCambio, Ubicacion


@admin.register(Ubicacion)
class UbicacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo', 'padre', 'edificio', 'salon')
    list_filter = ('tipo',)
    search_fields = ('nombre', 'edificio', 'salon')


@admin.register(Equipo)
class EquipoAdmin(SimpleHistoryAdmin):
    list_display = (
        'tipo', 'tipo_otro', 'aula', 'marca', 'modelo', 'numero_serie',
        'ubicacion', 'responsable', 'estado', 'valor', 'fecha_registro',
    )
    list_filter = ('tipo', 'estado', 'ubicacion', 'aula')
    search_fields = ('marca', 'modelo', 'numero_serie', 'responsable', 'direccion_ip', 'tipo_otro', 'aula', 'procesador', 'ram', 'so', 'almacenamiento')
    list_select_related = ('ubicacion',)


@admin.register(HistorialCambio)
class HistorialCambioAdmin(admin.ModelAdmin):
    list_display = ('equipo', 'campo', 'usuario', 'fecha')
    list_filter = ('campo', 'fecha')
    search_fields = ('equipo__numero_serie', 'equipo__marca', 'campo')
    date_hierarchy = 'fecha'
    readonly_fields = ('equipo', 'usuario', 'campo', 'valor_anterior', 'valor_nuevo', 'fecha')