from django.urls import path
from . import views

app_name = 'mesa_ayuda'

urlpatterns = [
    path('', views.IncidenciaListView.as_view(), name='lista'),
    path('nueva/', views.IncidenciaCreateView.as_view(), name='nueva'),
    path('<int:pk>/', views.IncidenciaDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.IncidenciaUpdateView.as_view(), name='editar'),
    path('<int:pk>/asignar/', views.IncidenciaAsignarView.as_view(), name='asignar'),
    path('<int:pk>/comentar/', views.ComentarioCreateView.as_view(), name='comentar'),
]