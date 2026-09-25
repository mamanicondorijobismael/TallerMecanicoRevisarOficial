from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.dashboard_reportes, name='dashboard'),
    path('diario/', views.reporte_diario, name='diario'),
    path('movimientos/', views.reporte_movimientos, name='movimientos'),
]
