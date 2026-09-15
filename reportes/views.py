from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import JsonResponse
from django.utils import timezone
from django.utils.formats import date_format
from django.views.generic import TemplateView, View

from inventario.models import Equipo, Ubicacion
from mantenimiento.models import Mantenimiento
from mesa_ayuda.models import Incidencia


class ReportesDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/reportes_dashboard.html'


class ReporteInventarioView(LoginRequiredMixin, TemplateView):
    template_name = 'reportes/reporte_inventario.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        estado = self.request.GET.get('estado')
        tipo = self.request.GET.get('tipo')
        area = self.request.GET.get('area')

        equipos = Equipo.objects.select_related('ubicacion').all()
        if estado in dict(Equipo.ESTADO_CHOICES):
            equipos = equipos.filter(estado=estado)
        if tipo in dict(Equipo.TIPO_CHOICES):
            equipos = equipos.filter(tipo=tipo)
        if area and area.isdigit():
            equipos = equipos.filter(ubicacion_id=area)

        context['equipos'] = equipos
        context['total_valor'] = equipos.aggregate(total=Sum('valor'))['total'] or 0
        context['total_equipos'] = equipos.count()
        context['estado'] = estado
        context['tipo_reporte'] = tipo
        context['area_reporte'] = area
        context['fecha_reporte'] = timezone.now()
        context['estado_choices'] = Equipo.ESTADO_CHOICES
        context['tipo_choices'] = Equipo.TIPO_CHOICES
        context['ubicaciones_lista'] = Ubicacion.objects.all()
        return context


class EquiposPorUbicacionAPI(LoginRequiredMixin, View):
    def get(self, request):
        data = (
            Equipo.objects
            .values('ubicacion__nombre')
            .annotate(total=Count('id'))
            .order_by('ubicacion__nombre')
        )
        labels = [item['ubicacion__nombre'] for item in data]
        values = [item['total'] for item in data]
        return JsonResponse({'labels': labels, 'data': values})


class EquiposPorEstadoAPI(LoginRequiredMixin, View):
    def get(self, request):
        ESTADO_MAP = dict(Equipo.ESTADO_CHOICES)
        data = (
            Equipo.objects
            .values('estado')
            .annotate(total=Count('id'))
            .order_by('estado')
        )
        labels = [ESTADO_MAP.get(item['estado'], item['estado']) for item in data]
        values = [item['total'] for item in data]
        return JsonResponse({'labels': labels, 'data': values})


class IncidenciasPorMesAPI(LoginRequiredMixin, View):
    def get(self, request):
        hoy = timezone.now().date()
        inicio = hoy - timedelta(days=365)
        data = (
            Incidencia.objects
            .filter(fecha_creacion__date__gte=inicio)
            .annotate(anio=ExtractYear('fecha_creacion'), mes=ExtractMonth('fecha_creacion'))
            .values('anio', 'mes')
            .annotate(total=Count('id'))
            .order_by('anio', 'mes')
        )
        labels = []
        values = []
        for item in data:
            dt = date(item['anio'], item['mes'], 1)
            labels.append(date_format(dt, 'M Y'))
            values.append(item['total'])
        return JsonResponse({'labels': labels, 'data': values})


class IncidenciasPorPrioridadAPI(LoginRequiredMixin, View):
    def get(self, request):
        PRIORIDAD_MAP = dict(Incidencia.PRIORIDAD_CHOICES)
        data = (
            Incidencia.objects
            .values('prioridad')
            .annotate(total=Count('id'))
            .order_by('prioridad')
        )
        labels = [PRIORIDAD_MAP.get(item['prioridad'], item['prioridad']) for item in data]
        values = [item['total'] for item in data]
        return JsonResponse({'labels': labels, 'data': values})


class EquiposMasFallasAPI(LoginRequiredMixin, View):
    def get(self, request):
        data = (
            Equipo.objects
            .annotate(num_fallas=Count('incidencias'))
            .filter(num_fallas__gt=0)
            .order_by('-num_fallas')[:10]
        )
        labels = [str(equipo) for equipo in data]
        values = [equipo.num_fallas for equipo in data]
        return JsonResponse({'labels': labels, 'data': values})


class MantenimientosPorPeriodoAPI(LoginRequiredMixin, View):
    def get(self, request):
        hoy = timezone.now().date()
        inicio = hoy - timedelta(days=365)
        data = (
            Mantenimiento.objects
            .filter(fecha_programada__gte=inicio)
            .annotate(anio=ExtractYear('fecha_programada'), mes=ExtractMonth('fecha_programada'))
            .values('anio', 'mes')
            .annotate(total=Count('id'))
            .order_by('anio', 'mes')
        )
        labels = []
        values = []
        for item in data:
            dt = date(item['anio'], item['mes'], 1)
            labels.append(date_format(dt, 'M Y'))
            values.append(item['total'])
        return JsonResponse({'labels': labels, 'data': values})
