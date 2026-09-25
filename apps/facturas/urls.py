from django.urls import path
from . import views

app_name = 'facturas'

urlpatterns = [
    path('', views.factura_list, name='lista'),
    path('<int:pk>/', views.factura_detalle, name='detalle'),
    path('generar/<int:orden_pk>/', views.generar_factura, name='generar'),
    path('<int:pk>/pago/', views.registrar_pago, name='pago'),
]
