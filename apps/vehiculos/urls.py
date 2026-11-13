from django.urls import path
from . import views

app_name = 'vehiculos'

urlpatterns = [
    path('', views.vehiculo_list, name='lista'),
    path('nuevo/', views.vehiculo_crear, name='crear'),
    path('<int:pk>/', views.vehiculo_detalle, name='detalle'),
    path('<int:pk>/editar/', views.vehiculo_editar, name='editar'),
    path('<int:pk>/eliminar/',views.vehiculo_eliminar, name='eliminar'),
]
