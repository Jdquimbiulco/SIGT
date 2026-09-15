def sidebar_context(request):
    user = request.user
    items = []

    if not user.is_authenticated:
        return {'sidebar_items': []}

    items.append({'label': 'Dashboard', 'url': '/', 'icon': 'bi-speedometer2'})

    if user.has_perm('inventario.view_equipo'):
        items.append({'label': 'Inventario', 'url': '/inventario/', 'icon': 'bi-pc-display'})

    if user.has_perm('mesa_ayuda.view_incidencia'):
        items.append({'label': 'Mesa de Ayuda', 'url': '/mesa-ayuda/', 'icon': 'bi-tools'})

    if user.has_perm('mantenimiento.view_mantenimiento'):
        items.append({'label': 'Mantenimiento', 'url': '/mantenimiento/', 'icon': 'bi-wrench-adjustable'})

    if user.is_authenticated:
        items.append({'label': 'Reportes', 'url': '/reportes/', 'icon': 'bi-graph-up'})

    if user.has_perm('usuarios.view_user') or user.is_superuser:
        items.append({'label': 'Usuarios', 'url': '/usuarios/', 'icon': 'bi-people'})

    return {'sidebar_items': items}
