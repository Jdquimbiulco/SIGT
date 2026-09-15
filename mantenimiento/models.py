from django.db import models
from django.conf import settings


class Mantenimiento(models.Model):
    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]
    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    ]

    equipo = models.ForeignKey(
        'inventario.Equipo', on_delete=models.CASCADE, related_name='mantenimientos'
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    fecha_programada = models.DateField()
    fecha_realizada = models.DateField(null=True, blank=True)
    tecnico = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='mantenimientos_asignados'
    )
    observaciones = models.TextField(blank=True)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='programado')
    historial = models.TextField(blank=True, help_text='Registro de pasos realizados')

    class Meta:
        ordering = ['fecha_programada']
        permissions = [
            ('puede_programar_mantenimiento', 'Puede programar mantenimientos'),
        ]

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.equipo} ({self.fecha_programada})'

    @property
    def proximo_a_vencer(self):
        from django.utils import timezone
        from datetime import timedelta
        if self.estado == 'programado':
            diff = self.fecha_programada - timezone.now().date()
            return diff.days <= 3
        return False
