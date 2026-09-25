from django.urls import path
from . import views

app_name = 'reservas'

urlpatterns = [
    path('', views.reserva_list, name='lista'),
    path('nueva/', views.reserva_crear, name='crear'),
    path('<int:pk>/editar/', views.reserva_editar, name='editar'),
]
