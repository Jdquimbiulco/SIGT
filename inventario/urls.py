from django.urls import path

from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.EquipoListView.as_view(), name='lista'),
    path('nuevo/', views.EquipoCreateView.as_view(), name='nuevo'),
    path('<int:pk>/', views.EquipoDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EquipoUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EquipoDeleteView.as_view(), name='eliminar'),
    path('ubicaciones/', views.UbicacionListView.as_view(), name='ubicaciones'),
    path('ubicaciones/nueva/', views.UbicacionCreateView.as_view(), name='ubicacion_nueva'),
    path('ubicaciones/<int:pk>/', views.UbicacionDetailView.as_view(), name='ubicacion_detalle'),
    path('ubicaciones/<int:pk>/editar/', views.UbicacionUpdateView.as_view(), name='ubicacion_editar'),
    path('ubicaciones/<int:pk>/eliminar/', views.UbicacionDeleteView.as_view(), name='ubicacion_eliminar'),
]