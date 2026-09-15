from datetime import date, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.db.models.functions import ExtractMonth, ExtractYear
from django.http import Http404, HttpResponse, JsonResponse
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


def _equipos_filtrados(request):
    estado = request.GET.get('estado')
    tipo = request.GET.get('tipo')
    area = request.GET.get('area')

    equipos = Equipo.objects.select_related('ubicacion').all()
    if estado in dict(Equipo.ESTADO_CHOICES):
        equipos = equipos.filter(estado=estado)
    if tipo in dict(Equipo.TIPO_CHOICES):
        equipos = equipos.filter(tipo=tipo)
    if area and area.isdigit():
        equipos = equipos.filter(ubicacion_id=area)
    return equipos


class ReporteInventarioExcelView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            import openpyxl
        except ImportError:
            raise Http404('openpyxl no está instalado.')

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Inventario'

        encabezados = [
            '#', 'Área', 'Marca', 'Modelo', 'Tipo',
            'Procesador', 'RAM', 'Sistema Operativo', 'Almacenamiento', 'Valor ($)',
        ]
        ws.append(encabezados)
        for cell in ws[1]:
            cell.font = openpyxl.styles.Font(bold=True)

        for i, equipo in enumerate(_equipos_filtrados(request), start=1):
            ws.append([
                i,
                equipo.ubicacion.nombre if equipo.ubicacion else '',
                equipo.marca,
                equipo.modelo,
                equipo.tipo_display,
                equipo.procesador or '',
                equipo.ram or '',
                equipo.so or '',
                equipo.almacenamiento or '',
                float(equipo.valor) if equipo.valor is not None else None,
            ])

        total = _equipos_filtrados(request).aggregate(total=Sum('valor'))['total'] or 0
        ws.append([f'Valor Total ({len(encabezados) - 1})', '', '', '', '', '', '', '', 'Total', float(total)])

        ws.column_dimensions['A'].width = 5
        for col, w in zip('BCDEFGHIJ', (18, 18, 22, 16, 22, 10, 18, 16, 12)):
            ws.column_dimensions[col].width = w

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="reporte_inventario.xlsx"'
        wb.save(response)
        return response


class ReporteInventarioPDFView(LoginRequiredMixin, View):
    def get(self, request):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.units import mm
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
        except ImportError:
            raise Http404('reportlab no está instalado.')

        equipos = list(_equipos_filtrados(request))
        total = _equipos_filtrados(request).aggregate(total=Sum('valor'))['total'] or 0

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_inventario.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            leftMargin=10 * mm, rightMargin=10 * mm,
            topMargin=12 * mm, bottomMargin=12 * mm,
        )
        styles = getSampleStyleSheet()
        elementos = []
        elementos.append(Paragraph('SIGT - Reporte de Inventario de Equipos', styles['Title']))
        elementos.append(Spacer(1, 4 * mm))
        elementos.append(Paragraph(
            f"Generado el {date_format(timezone.now(), 'd/m/Y H:i')} — Total de equipos: {len(equipos)}",
            styles['Normal'],
        ))
        elementos.append(Spacer(1, 6 * mm))

        encabezados = [
            '#', 'Área', 'Marca', 'Modelo', 'Tipo',
            'Procesador', 'RAM', 'SO', 'Almac. (GB)', 'Valor ($)',
        ]
        filas = [encabezados]
        for i, equipo in enumerate(equipos, start=1):
            filas.append([
                str(i),
                equipo.ubicacion.nombre if equipo.ubicacion else '',
                equipo.marca,
                equipo.modelo,
                equipo.tipo_display,
                equipo.procesador or '',
                equipo.ram or '',
                equipo.so or '',
                equipo.almacenamiento or '',
                f"{float(equipo.valor):.2f}" if equipo.valor is not None else '',
            ])
        filas.append([
            f'Valor Total ({len(equipos)})', '', '', '', '', '', '', '', 'Total', f"{float(total):.2f}",
        ])

        tabla = Table(filas, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('GRID', (0, 0), (-1, -2), 0.4, colors.grey),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f1f5f9')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elementos.append(tabla)

        doc.build(elementos)
        return response


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
