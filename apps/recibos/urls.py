from django.urls import path
from . import views

app_name = 'recibos'

urlpatterns = [
    path('', views.recibo_lista, name='lista'),
    path('<int:pk>/', views.recibo_detalle, name='detalle'),
    path('generar/<int:orden_pk>/', views.generar_recibo, name='generar'),
    path('<int:pk>/pago/', views.registrar_pago, name='pago'),
    path('<int:pk>/anular/', views.anular_recibo, name='anular'),
    path('<int:pk>/imprimir/', views.imprimir_recibo, name='imprimir'),
]
