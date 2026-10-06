from django.urls import path
from . import views

app_name = 'mantenimiento'

urlpatterns = [
    path('', views.alerta_list, name='alertas'),
    path('nueva/', views.alerta_crear, name='crear'),
    path('<int:pk>/estado/<str:estado>/', views.alerta_cambiar_estado, name='cambiar_estado'),
    path('<int:pk>/eliminar/', views.alerta_eliminar, name='eliminar'),
    path('tipos/', views.tipo_servicio_list, name='tipos'),
    path('tipos/nuevo/', views.tipo_servicio_crear, name='tipo_crear'),
    path('tipos/<int:pk>/editar/', views.tipo_servicio_editar, name='tipo_editar'),
    path('tipos/<int:pk>/eliminar/', views.tipo_servicio_eliminar, name='tipo_eliminar'),
]
