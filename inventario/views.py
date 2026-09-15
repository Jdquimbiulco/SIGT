from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import EquipoForm, UbicacionForm
from .models import Equipo, HistorialCambio, Ubicacion

CAMPOS_REGISTRABLES = [
    'tipo', 'tipo_otro', 'aula', 'marca', 'modelo', 'numero_serie', 'direccion_ip',
    'ubicacion', 'responsable', 'estado', 'observaciones',
    'procesador', 'ram', 'so', 'almacenamiento', 'valor',
]


def _registrar_cambios(equipo, usuario, origen=None):
    for campo in CAMPOS_REGISTRABLES:
        valor_anterior = str(getattr(origen, campo, '') or '') if origen else ''
        valor_nuevo = str(getattr(equipo, campo) or '')
        if valor_anterior != valor_nuevo:
            HistorialCambio.objects.create(
                equipo=equipo,
                usuario=usuario,
                campo=campo,
                valor_anterior=valor_anterior,
                valor_nuevo=valor_nuevo,
            )


class EquipoListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Equipo
    template_name = 'inventario/equipo_list.html'
    context_object_name = 'equipos'
    permission_required = 'inventario.view_equipo'

    def get_queryset(self):
        queryset = Equipo.objects.select_related('ubicacion').all()
        estado = self.request.GET.get('estado')
        tipo = self.request.GET.get('tipo')
        ubicacion = self.request.GET.get('ubicacion')
        aula = self.request.GET.get('aula')
        if estado in dict(Equipo.ESTADO_CHOICES):
            queryset = queryset.filter(estado=estado)
        if tipo in dict(Equipo.TIPO_CHOICES):
            queryset = queryset.filter(tipo=tipo)
        if ubicacion and ubicacion.isdigit():
            try:
                ubicacion_obj = Ubicacion.objects.get(pk=int(ubicacion))
                queryset = queryset.filter(
                    ubicacion_id__in=ubicacion_obj.equipos_incluyendo_hijos().values('ubicacion_id').distinct()
                )
                if aula:
                    queryset = queryset.filter(aula=aula)
            except Ubicacion.DoesNotExist:
                pass
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_choices'] = Equipo.ESTADO_CHOICES
        context['tipo_choices'] = Equipo.TIPO_CHOICES
        context['filtro_estado'] = self.request.GET.get('estado', '')
        context['filtro_tipo'] = self.request.GET.get('tipo', '')
        context['filtro_ubicacion'] = self.request.GET.get('ubicacion', '')
        context['filtro_aula'] = self.request.GET.get('aula', '')
        context['ubicaciones_lista'] = Ubicacion.objects.all()
        context['aulas_disponibles'] = self._aulas_de_ubicacion(context['filtro_ubicacion'])
        return context

    def _aulas_de_ubicacion(self, ubicacion_pk):
        if not ubicacion_pk or not ubicacion_pk.isdigit():
            return []
        try:
            Ubicacion.objects.get(pk=int(ubicacion_pk))
        except Ubicacion.DoesNotExist:
            return []
        aulas = (
            self.get_queryset()
            .exclude(aula='')
            .values_list('aula', flat=True)
            .distinct()
        )
        return sorted(aulas, key=lambda a: (len(a), a))


class EquipoFormMixin:
    form_class = EquipoForm
    template_name = 'inventario/equipo_form.html'
    title = 'Equipo'

    def get_success_url(self):
        return reverse('inventario:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        es_nuevo = not (getattr(self, 'object', None) and self.object.pk)
        anterior = Equipo.objects.get(pk=self.object.pk) if not es_nuevo else None
        self.object = form.save()
        if self.request.user.is_authenticated:
            _registrar_cambios(self.object, self.request.user, anterior)
        if es_nuevo:
            messages.success(self.request, 'Equipo creado correctamente.')
        else:
            messages.success(self.request, 'Equipo actualizado correctamente.')
        return redirect(self.get_success_url())


class EquipoCreateView(LoginRequiredMixin, PermissionRequiredMixin, EquipoFormMixin, CreateView):
    model = Equipo
    permission_required = 'inventario.add_equipo'
    title = 'Nuevo Equipo'


class EquipoUpdateView(LoginRequiredMixin, PermissionRequiredMixin, EquipoFormMixin, UpdateView):
    model = Equipo
    permission_required = 'inventario.change_equipo'
    title = 'Editar Equipo'


class EquipoDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Equipo
    template_name = 'inventario/equipo_detail.html'
    context_object_name = 'equipo'
    permission_required = 'inventario.view_equipo'

    def get_queryset(self):
        return Equipo.objects.select_related('ubicacion').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['historial_cambios'] = (
            self.object.cambios.select_related('usuario')[:20]
        )
        return context


class EquipoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Equipo
    template_name = 'inventario/equipo_confirm_delete.html'
    context_object_name = 'equipo'
    permission_required = 'inventario.delete_equipo'
    success_url = reverse_lazy('inventario:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Equipo eliminado correctamente.')
        return super().form_valid(form)


class UbicacionListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Ubicacion
    template_name = 'inventario/ubicacion_list.html'
    context_object_name = 'ubicaciones'
    permission_required = 'inventario.view_ubicacion'

    def get_queryset(self):
        return Ubicacion.objects.select_related('padre').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['raices'] = [u for u in context['ubicaciones'] if u.padre is None]
        context['tipo_choices'] = Ubicacion.TIPO_CHOICES
        return context


class UbicacionDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Ubicacion
    template_name = 'inventario/ubicacion_detail.html'
    context_object_name = 'ubicacion'
    permission_required = 'inventario.view_ubicacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['equipos'] = self.object.equipos_incluyendo_hijos().select_related('ubicacion')
        context['sububicaciones'] = self.object.sububicaciones.all()
        return context


class UbicacionCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Ubicacion
    form_class = UbicacionForm
    template_name = 'inventario/ubicacion_form.html'
    permission_required = 'inventario.add_ubicacion'
    success_url = reverse_lazy('inventario:ubicaciones')
    title = 'Nueva Ubicación'

    def get_initial(self):
        initial = super().get_initial()
        padre = self.request.GET.get('padre')
        if padre and padre.isdigit():
            try:
                initial['padre'] = Ubicacion.objects.get(pk=int(padre))
            except Ubicacion.DoesNotExist:
                pass
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Ubicación creada correctamente.')
        return super().form_valid(form)


class UbicacionUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Ubicacion
    form_class = UbicacionForm
    template_name = 'inventario/ubicacion_form.html'
    permission_required = 'inventario.change_ubicacion'
    title = 'Editar Ubicación'

    def get_success_url(self):
        return reverse_lazy('inventario:ubicaciones')

    def form_valid(self, form):
        messages.success(self.request, 'Ubicación actualizada correctamente.')
        return super().form_valid(form)


class UbicacionDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Ubicacion
    template_name = 'inventario/ubicacion_confirm_delete.html'
    context_object_name = 'ubicacion'
    permission_required = 'inventario.delete_ubicacion'
    success_url = reverse_lazy('inventario:ubicaciones')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'No se pudo eliminar "{self.object.nombre}" porque tiene equipos u otras referencias asociadas.',
            )
            return redirect(reverse_lazy('inventario:ubicacion_detalle', kwargs={'pk': self.object.pk}))
        messages.success(self.request, 'Ubicación eliminada correctamente.')
        return response