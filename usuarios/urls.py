from django.urls import path
from django.contrib.auth.views import LogoutView

from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', views.UserListView.as_view(), name='lista'),
    path('nuevo/', views.UserCreateView.as_view(), name='nuevo'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.UserUpdateView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.UserDeleteView.as_view(), name='eliminar'),
]