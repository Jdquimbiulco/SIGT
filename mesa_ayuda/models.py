from django.db import models
from django.conf import settings
from django.utils import timezone


class Incidencia(models.Model):
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    ESTADO_CHOICES = [
        ('abierta', 'Abierta'),
        ('en_proceso', 'En Proceso'),
        ('resuelta', 'Resuelta'),
        ('cerrada', 'Cerrada'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    nombre_reportero = models.CharField(max_length=150, blank=True, help_text='Nombre de quien reporta (si no es usuario del sistema)')
    area = models.CharField(max_length=100, blank=True, help_text='Salón / área donde ocurrió la falla')
    contacto = models.CharField(max_length=100, blank=True, help_text='Email o teléfono de contacto del reportero')
    equipo = models.ForeignKey(
        'inventario.Equipo', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='incidencias'
    )
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='abierta')
    tecnico_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='incidencias_asignadas'
    )
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='incidencias_creadas'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_creacion']
        permissions = [
            ('puede_cerrar_incidencia', 'Puede cerrar incidencias'),
        ]

    def __str__(self):
        return f'#{self.pk} - {self.titulo}'

    @property
    def prioridad_color(self):
        return {'baja': 'info', 'media': 'warning', 'alta': 'danger', 'urgente': 'dark'}.get(self.prioridad, 'secondary')

    @property
    def estado_color(self):
        return {
            'abierta': 'danger', 'en_proceso': 'warning',
            'resuelta': 'success', 'cerrada': 'secondary'
        }.get(self.estado, 'secondary')

    def save(self, *args, **kwargs):
        if self.estado in ('resuelta', 'cerrada') and not self.fecha_resolucion:
            self.fecha_resolucion = timezone.now()
        super().save(*args, **kwargs)


class Comentario(models.Model):
    incidencia = models.ForeignKey(Incidencia, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f'Comentario de {self.autor} en #{self.incidencia.pk}'
