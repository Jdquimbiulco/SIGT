from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import ListView, CreateView, DetailView, UpdateView
from datetime import timedelta

from .forms import MantenimientoForm, MantenimientoCompletarForm
from .models import Mantenimiento


class MantenimientoListView(LoginRequiredMixin, ListView):
    model = Mantenimiento
    template_name = 'mantenimiento/mantenimiento_list.html'
    context_object_name = 'mantenimientos'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        estado = self.request.GET.get('estado', '')
        tipo = self.request.GET.get('tipo', '')
        if estado:
            qs = qs.filter(estado=estado)
        if tipo:
            qs = qs.filter(tipo=tipo)
        return qs.select_related('equipo', 'tecnico').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estado_choices'] = Mantenimiento.ESTADO_CHOICES
        context['tipo_choices'] = Mantenimiento.TIPO_CHOICES
        context['filtro_estado'] = self.request.GET.get('estado', '')
        context['filtro_tipo'] = self.request.GET.get('tipo', '')
        return context


class MantenimientoCreateView(LoginRequiredMixin, CreateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'mantenimiento/mantenimiento_form.html'
    success_url = reverse_lazy('mantenimiento:lista')

    def form_valid(self, form):
        messages.success(self.request, 'Mantenimiento registrado correctamente.')
        return super().form_valid(form)


class MantenimientoDetailView(LoginRequiredMixin, DetailView):
    model = Mantenimiento
    template_name = 'mantenimiento/mantenimiento_detail.html'
    context_object_name = 'mantenimiento'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completar_form'] = MantenimientoCompletarForm(
            initial={'fecha_realizada': timezone.now().date()}
        )
        return context


class MantenimientoUpdateView(LoginRequiredMixin, UpdateView):
    model = Mantenimiento
    form_class = MantenimientoForm
    template_name = 'mantenimiento/mantenimiento_form.html'

    def get_success_url(self):
        return reverse_lazy('mantenimiento:detalle', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Mantenimiento actualizado correctamente.')
        return super().form_valid(form)


class MantenimientoCompletarView(LoginRequiredMixin, View):

    def post(self, request, pk):
        mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
        form = MantenimientoCompletarForm(request.POST)
        if form.is_valid():
            mantenimiento.estado = 'completado'
            mantenimiento.fecha_realizada = form.cleaned_data['fecha_realizada']
            obs = form.cleaned_data.get('observaciones_final', '').strip()
            timestamp = timezone.now().strftime('%d/%m/%Y %H:%M')
            entrada = f'[{timestamp}] Completado.' + (f' {obs}' if obs else '')
            if mantenimiento.historial:
                mantenimiento.historial = f'{mantenimiento.historial}\n{entrada}'
            else:
                mantenimiento.historial = entrada
            mantenimiento.save()
            messages.success(request, 'Mantenimiento marcado como completado.')
        else:
            messages.error(request, 'No se pudo completar el mantenimiento.')
        return redirect('mantenimiento:detalle', pk=pk)


class MantenimientoAlertasView(LoginRequiredMixin, ListView):
    model = Mantenimiento
    template_name = 'mantenimiento/alertas_list.html'
    context_object_name = 'alertas'

    def get_queryset(self):
        hoy = timezone.now().date()
        limite = hoy + timedelta(days=7)
        # programas: proximos_a_vencer (<=3 días) o con fecha en los próximos 7 días
        return Mantenimiento.objects.filter(
            Q(estado='programado', fecha_programada__lte=limite)
        ).select_related('equipo', 'tecnico').order_by('fecha_programada')