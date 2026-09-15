from django.contrib import admin
from .models import Mantenimiento


@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = [
        'equipo', 'tipo', 'fecha_programada', 'fecha_realizada',
        'tecnico', 'estado',
    ]
    list_filter = ['estado', 'tipo', 'fecha_programada']
    search_fields = ['equipo__marca', 'equipo__modelo', 'tecnico__first_name', 'tecnico__last_name']
    date_hierarchy = 'fecha_programada'
    list_editable = ['estado']
    ordering = ['fecha_programada']
