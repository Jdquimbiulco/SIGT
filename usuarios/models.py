from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('tecnico', 'Técnico'),
    ]

    rol = models.CharField(max_length=10, choices=ROL_CHOICES, default='tecnico')
    telefono = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'

    def __str__(self):
        return f'{self.get_full_name() or self.username}'

    @property
    def is_admin_rol(self):
        return self.rol == 'admin'

    @property
    def is_tecnico_rol(self):
        return self.rol == 'tecnico'

    @property
    def is_consulta_rol(self):
        return self.rol == 'consulta'
