from django.urls import path
from . import views

app_name = 'ordenes'

urlpatterns = [
    path('', views.orden_list, name='lista'),
    path('nueva/', views.orden_crear, name='crear'),
    path('<int:pk>/', views.orden_detalle, name='detalle'),
    path('<int:pk>/editar/', views.orden_editar, name='editar'),
    path('<int:pk>/estado/', views.orden_cambiar_estado, name='cambiar_estado'),
    path('<int:pk>/servicios/agregar/', views.agregar_servicio, name='agregar_servicio'),
    path('<int:pk>/servicios/<int:spk>/eliminar/', views.eliminar_servicio, name='eliminar_servicio'),
    path('<int:pk>/productos/agregar/', views.agregar_producto, name='agregar_producto'),
    path('<int:pk>/productos/<int:ppk>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
]
