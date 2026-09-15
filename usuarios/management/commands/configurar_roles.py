from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from usuarios.models import User

APPS_TECNICO = ['inventario', 'mesa_ayuda', 'mantenimiento', 'reportes']
APPS_ADMIN = ['inventario', 'mesa_ayuda', 'mantenimiento', 'reportes', 'usuarios']


class Command(BaseCommand):
    help = 'Crea los grupos de roles y asigna permisos según el rol definido en cada usuario.'

    def handle(self, *args, **options):
        self.stdout.write('Creando grupos...')

        admin_group, _ = Group.objects.get_or_create(name='Administrador')
        tecnico_group, _ = Group.objects.get_or_create(name='Técnico')

        for perm in Permission.objects.filter(content_type__app_label__in=APPS_ADMIN):
            admin_group.permissions.add(perm)

        for perm in Permission.objects.filter(content_type__app_label__in=APPS_TECNICO):
            tecnico_group.permissions.add(perm)

        self.stdout.write('Asignando grupos según rol de cada usuario...')
        for user in User.objects.filter(rol__in=['admin', 'tecnico']):
            user.groups.clear()
            if user.is_admin_rol:
                user.groups.add(admin_group)
            elif user.is_tecnico_rol:
                user.groups.add(tecnico_group)

        self.stdout.write(self.style.SUCCESS('Roles configurados correctamente.'))