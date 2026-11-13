from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

admin.site.site_header = "Taller Mecanico y Gomeria - Admin"
admin.site.site_title = "Taller Admin"
admin.site.index_title = "Panel de Administracion"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.accounts.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('vehiculos/', include('apps.vehiculos.urls')),
    path('inventario/', include('apps.inventario.urls')),
    path('ordenes/', include('apps.ordenes.urls')),
    path('recibos/', include('apps.recibos.urls')),
    path('comprobantes/', lambda request: redirect('recibos:lista')),
    path('reportes/', include('apps.reportes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
