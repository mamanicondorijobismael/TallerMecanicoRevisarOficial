from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('diario/', views.reporte_diario, name='diario'),
    path('diario/exportar-csv/', views.exportar_cierre_diario_csv, name='exportar_diario_csv'),
    path('movimientos/', views.reporte_movimientos, name='movimientos'),
    path('movimientos/exportar-csv/', views.exportar_movimientos_csv, name='exportar_movimientos_csv'),
]
