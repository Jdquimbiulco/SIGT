from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    path('', views.MantenimientoListView.as_view(), name='lista'),
    path('nuevo/', views.MantenimientoCreateView.as_view(), name='nuevo'),
    path('<int:pk>/', views.MantenimientoDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.MantenimientoUpdateView.as_view(), name='editar'),
    path('<int:pk>/completar/', views.MantenimientoCompletarView.as_view(), name='completar'),
    path('alertas/', views.MantenimientoAlertasView.as_view(), name='alertas'),
]
