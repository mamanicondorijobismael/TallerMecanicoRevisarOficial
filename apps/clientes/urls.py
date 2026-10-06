from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('', views.cliente_list, name='lista'),
    path('nuevo/', views.cliente_crear, name='crear'),
    path('<int:pk>/', views.cliente_detalle, name='detalle'),
    path('<int:pk>/editar/', views.cliente_editar, name='editar'),
    path('<int:pk>/eliminar/', views.cliente_eliminar, name='eliminar'),
]
