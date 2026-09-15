from django.db import models
from django.conf import settings
from simple_history.models import HistoricalRecords


class Ubicacion(models.Model):
    TIPO_CHOICES = [
        ('sede', 'Sede'),
        ('etapa', 'Etapa'),
        ('salon', 'Salón'),
        ('laboratorio', 'Laboratorio'),
        ('oficina', 'Oficina'),
        ('otro', 'Otro'),
    ]

    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='salon')
    padre = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True,
        related_name='sububicaciones', verbose_name='Pertenece a',
        help_text='Nivel superior (ej: un Salón pertenece a una Etapa)'
    )
    edificio = models.CharField(max_length=100, blank=True)
    salon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name_plural = 'Ubicaciones'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def nombre_completo(self):
        if self.padre:
            return f'{self.padre.nombre} → {self.nombre}'
        return self.nombre

    @property
    def total_equipos_directos(self):
        return self.equipos.count()

    @property
    def total_equipos(self):
        return self.equipos_incluyendo_hijos().count()

    def _descendientes_ids(self, ids):
        hijos = self.sububicaciones.all()
        for hijo in hijos:
            ids.append(hijo.pk)
            hijo._descendientes_ids(ids)
        return ids

    def equipos_incluyendo_hijos(self):
        ids = self._descendientes_ids([self.pk])
        return Equipo.objects.filter(ubicacion_id__in=ids)


class Equipo(models.Model):
    TIPO_CHOICES = [
        ('computadora', 'Computadora'),
        ('laptop', 'Laptop'),
        ('proyector', 'Proyector'),
        ('impresora', 'Impresora'),
        ('access_point', 'Access Point'),
        ('switch', 'Switch'),
        ('otro', 'Otro (especificar)'),
    ]
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('mantenimiento', 'En Mantenimiento'),
        ('baja', 'Dado de Baja'),
    ]

    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    tipo_otro = models.CharField(
        max_length=100, blank=True,
        help_text='Especifique el tipo si seleccionó "Otro"'
    )
    aula = models.CharField(
        max_length=10, blank=True,
        help_text='Aula dentro de la ubicación. Ej: 01, 05, 13'
    )
    procesador = models.CharField(max_length=100, blank=True, verbose_name='Procesador')
    ram = models.CharField(max_length=50, blank=True, verbose_name='Memoria RAM')
    so = models.CharField(max_length=100, blank=True, verbose_name='Sistema operativo')
    almacenamiento = models.CharField(max_length=50, blank=True, verbose_name='Almacenamiento')
    valor = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        verbose_name='Valor ($)',
        help_text='Valor económico del equipo (no obligatorio)'
    )
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=100, unique=True)
    direccion_ip = models.GenericIPAddressField(blank=True, null=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.PROTECT, related_name='equipos')
    responsable = models.CharField(max_length=150, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    fecha_registro = models.DateField(auto_now_add=True)
    observaciones = models.TextField(blank=True)
    historical = HistoricalRecords()

    class Meta:
        ordering = ['-fecha_registro']
        permissions = [
            ('puede_asignar_equipo', 'Puede asignar equipo a responsable'),
        ]

    def __str__(self):
        return f'{self.tipo_display} - {self.marca} {self.modelo}'

    @property
    def tipo_display(self):
        if self.tipo == 'otro' and self.tipo_otro:
            return self.tipo_otro
        return self.get_tipo_display()


class HistorialCambio(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='cambios')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    campo = models.CharField(max_length=50)
    valor_anterior = models.CharField(max_length=255, blank=True)
    valor_nuevo = models.CharField(max_length=255, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.equipo} - {self.campo}: {self.valor_anterior} → {self.valor_nuevo}'
