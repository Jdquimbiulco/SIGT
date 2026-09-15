from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView, CreateView, UpdateView, FormView, TemplateView
from django.contrib import messages

from .forms import IncidenciaForm, IncidenciaEstadoForm, ComentarioForm, IncidenciaPublicaForm
from .models import Incidencia, Comentario


class ReportarIncidenciaView(FormView):
    form_class = IncidenciaPublicaForm
    template_name = 'mesa_ayuda/reportar.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        return kwargs

    def form_valid(self, form):
        incidencia = form.save(commit=False)
        incidencia.estado = 'abierta'
        incidencia.prioridad = 'media'
        incidencia.creado_por = self.request.user if self.request.user.is_authenticated else None
        incidencia.save()
        return redirect('reporte_exitoso', pk=incidencia.pk)


class ReporteExitosoView(TemplateView):
    template_name = 'mesa_ayuda/reporte_exitoso.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['incidencia'] = get_object_or_404(Incidencia, pk=kwargs['pk'])
        return context


class IncidenciaListView(LoginRequiredMixin, ListView):
    model = Incidencia
    template_name = 'mesa_ayuda/incidencia_list.html'
    context_object_name = 'incidencias'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.GET.get('estado', '')
        prioridad = self.request.GET.get('prioridad', '')
        if estado:
            qs = qs.filter(estado=estado)
        if prioridad:
            qs = qs.filter(prioridad=prioridad)
        return qs.select_related('equipo', 'tecnico_asignado').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_choices'] = Incidencia.ESTADO_CHOICES
        context['prioridad_choices'] = Incidencia.PRIORIDAD_CHOICES
        return context


class IncidenciaCreateView(LoginRequiredMixin, CreateView):
    model = Incidencia
    form_class = IncidenciaForm
    template_name = 'mesa_ayuda/incidencia_form.html'
    success_url = reverse_lazy('mesa_ayuda:lista')

    def form_valid(self, form):
        form.instance.creado_por = self.request.user
        messages.success(self.request, 'Incidencia registrada correctamente.')
        return super().form_valid(form)


class IncidenciaDetailView(LoginRequiredMixin, DetailView):
    model = Incidencia
    template_name = 'mesa_ayuda/incidencia_detail.html'
    context_object_name = 'incidencia'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comentario_form'] = ComentarioForm()
        context['estado_form'] = IncidenciaEstadoForm()
        incidencia = self.get_object()
        context['can_change_estado'] = (
            self.request.user.has_perm('mesa_ayuda.change_incidencia')
            or (incidencia.tecnico_asignado is not None and incidencia.tecnico_asignado == self.request.user)
        )
        return context


class IncidenciaUpdateView(LoginRequiredMixin, UpdateView):
    model = Incidencia
    form_class = IncidenciaForm
    template_name = 'mesa_ayuda/incidencia_form.html'

    def get_success_url(self):
        return reverse_lazy('mesa_ayuda:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Incidencia actualizada correctamente.')
        return super().form_valid(form)


class IncidenciaAsignarView(LoginRequiredMixin, View):
    def post(self, request, pk=None):
        incidencia = get_object_or_404(Incidencia, pk=pk)
        tiene_permiso = request.user.has_perm('mesa_ayuda.change_incidencia')
        es_tecnico = incidencia.tecnico_asignado is not None and incidencia.tecnico_asignado == request.user
        if not (tiene_permiso or es_tecnico):
            messages.error(request, 'No tiene permisos para cambiar el estado de esta incidencia.')
            return redirect('mesa_ayuda:detalle', pk=incidencia.pk)
        form = IncidenciaEstadoForm(request.POST)
        if form.is_valid():
            incidencia.estado = form.cleaned_data['estado']
            incidencia.save()
            messages.success(request, f'Estado actualizado a "{incidencia.get_estado_display()}".')
        else:
            messages.error(request, 'No se pudo actualizar el estado.')
        return redirect('mesa_ayuda:detalle', pk=incidencia.pk)


class ComentarioCreateView(LoginRequiredMixin, CreateView):
    model = Comentario
    form_class = ComentarioForm

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.instance.incidencia = get_object_or_404(Incidencia, pk=self.kwargs['pk'])
        messages.success(self.request, 'Comentario agregado.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('mesa_ayuda:detalle', kwargs={'pk': self.kwargs['pk']})