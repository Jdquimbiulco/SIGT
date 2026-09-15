from django.core.management.base import BaseCommand
from inventario.models import Ubicacion

UBICACIONES_BASE = [
    ('Personales', 'otro'),
    ('Campito', 'sede'),
    ('Administración', 'oficina'),
    ('Laboratorio Basica Media', 'laboratorio'),
    ('Laboratorio Portátil', 'laboratorio'),
    ('Laboratorio Bachillerato', 'laboratorio'),
    ('Etapa 1', 'etapa'),
    ('Etapa 2', 'etapa'),
    ('Etapa 3', 'etapa'),
    ('Etapa 4', 'etapa'),
    ('Etapa 5', 'etapa'),
]


class Command(BaseCommand):
    help = 'Crea las ubicaciones base (Personales, Campito, Administración, etc.).'

    def handle(self, *args, **options):
        creadas = 0
        for nombre, tipo in UBICACIONES_BASE:
            _, was_created = Ubicacion.objects.get_or_create(
                nombre=nombre,
                defaults={'tipo': tipo, 'padre': None},
            )
            if was_created:
                creadas += 1
                self.stdout.write(f'  + {nombre}')
        self.stdout.write(self.style.SUCCESS(
            f'Ubicaciones base listas ({creadas} creadas, {len(UBICACIONES_BASE) - creadas} ya existían).'
        ))