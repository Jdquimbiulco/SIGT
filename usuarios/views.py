from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import LoginForm, UserCreationForm, UserEditForm
from .models import User

APPS_ADMIN = ['inventario', 'mesa_ayuda', 'mantenimiento', 'reportes', 'usuarios']

APPS_TECNICO = ['inventario', 'mesa_ayuda', 'mantenimiento', 'reportes']


def asignar_permisos_por_rol(user):
    user.user_permissions.clear()
    if user.rol == 'admin':
        user.user_permissions.set(
            Permission.objects.filter(content_type__app_label__in=APPS_ADMIN)
        )
        return
    user.user_permissions.set(
        Permission.objects.filter(content_type__app_label__in=APPS_TECNICO)
    )


class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = LoginForm


class PermisosUsuariosMixin(PermissionRequiredMixin):
    def has_permission(self):
        return super().has_permission() or self.request.user.is_superuser


class UserListView(LoginRequiredMixin, PermisosUsuariosMixin, ListView):
    model = User
    template_name = 'usuarios/user_list.html'
    context_object_name = 'usuarios'
    permission_required = 'usuarios.view_user'

    def get_queryset(self):
        qs = super().get_queryset()
        rol = self.request.GET.get('rol', '')
        if rol in dict(User.ROL_CHOICES):
            qs = qs.filter(rol=rol)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = User.ROL_CHOICES
        return context


class UserCreateView(LoginRequiredMixin, PermisosUsuariosMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'usuarios/user_form.html'
    permission_required = 'usuarios.add_user'
    success_url = reverse_lazy('usuarios:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        asignar_permisos_por_rol(self.object)
        messages.success(self.request, f'Usuario "{self.object.username}" creado correctamente.')
        return response


class UserDetailView(LoginRequiredMixin, PermisosUsuariosMixin, DetailView):
    model = User
    template_name = 'usuarios/user_detail.html'
    context_object_name = 'usuario'
    permission_required = 'usuarios.view_user'


class UserUpdateView(LoginRequiredMixin, PermisosUsuariosMixin, UpdateView):
    model = User
    form_class = UserEditForm
    template_name = 'usuarios/user_form.html'
    permission_required = 'usuarios.change_user'

    def get_success_url(self):
        return reverse_lazy('usuarios:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        asignar_permisos_por_rol(self.object)
        messages.success(self.request, f'Usuario "{self.object.username}" actualizado correctamente.')
        return response


class UserDeleteView(LoginRequiredMixin, PermisosUsuariosMixin, DeleteView):
    model = User
    template_name = 'usuarios/user_confirm_delete.html'
    permission_required = 'usuarios.delete_user'
    success_url = reverse_lazy('usuarios:lista')

    def form_valid(self, form):
        messages.success(self.request, f'Usuario "{self.object.username}" eliminado correctamente.')
        return super().form_valid(form)