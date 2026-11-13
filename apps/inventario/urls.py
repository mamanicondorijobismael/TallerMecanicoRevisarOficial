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
    path('llantas/', views.llanta_list, name='llantas'),
    path('llantas/nueva/', views.llanta_crear, name='llanta_crear'),
    path('llantas/<int:pk>/editar/', views.llanta_editar, name='llanta_editar'),
    path('<int:pk>/ajuste/', views.ajuste_stock, name='ajuste_stock'),
    path('movimientos/', views.movimientos_list, name='movimientos'),
    # Categorias
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nueva/', views.categoria_crear, name='categoria_crear'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/eliminar/', views.categoria_eliminar, name='categoria_eliminar'),
    path('<int:pk>/eliminar/', views.producto_eliminar, name='producto_eliminar'),
    path('ajax/buscar-repuestos/', views.ajax_buscar_repuestos, name='ajax_buscar_repuestos'),
    path('ajax/sugerir-sku/', views.ajax_sugerir_sku, name='ajax_sugerir_sku'),
]
