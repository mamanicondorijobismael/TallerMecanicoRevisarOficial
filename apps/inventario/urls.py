from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.producto_list, name='lista'),
    path('repuestos/', views.repuesto_list, name='repuestos'),
    path('repuestos/nuevo/', views.repuesto_crear, name='repuesto_crear'),
    path('repuestos/<int:pk>/editar/', views.repuesto_editar, name='repuesto_editar'),
    path('neumaticos/', views.neumatico_list, name='neumaticos'),
    path('neumaticos/nuevo/', views.neumatico_crear, name='neumatico_crear'),
    path('neumaticos/<int:pk>/editar/', views.neumatico_editar, name='neumatico_editar'),
    path('<int:pk>/venta/', views.venta_directa, name='venta_directa'),
    path('recibo/<int:pk>/', views.venta_recibo, name='venta_recibo'),
    path('<int:pk>/ajuste/', views.ajuste_stock, name='ajuste_stock'),
    path('movimientos/', views.movimientos_list, name='movimientos'),
    # Categorias
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
]
