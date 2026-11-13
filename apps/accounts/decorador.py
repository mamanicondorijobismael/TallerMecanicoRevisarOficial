from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def requiere_permiso(permiso, login_url='dashboard'):
    """
    Decorador estricto para restringir el acceso a vistas que requieren un privilegio
    específico configurado en la tabla de Roles (o superusuario).
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Debes iniciar sesión para acceder a esta sección.')
                return redirect('login')

            # Si es superusuario o tiene el permiso granular específico
            tiene = False
            if request.user.is_superuser:
                tiene = True
            elif hasattr(request.user, 'tiene_permiso'):
                tiene = request.user.tiene_permiso(permiso)
            elif request.user.rol and hasattr(request.user.rol, permiso):
                tiene = getattr(request.user.rol, permiso, False)

            if not tiene:
                messages.error(
                    request,
                    'Acceso Denegado: Tu rol de usuario no cuenta con el privilegio requerido para realizar esta acción.'
                )
                return redirect(login_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(login_url='dashboard'):
    """
    Decorador para restringir el acceso a vistas operativas que requieren
    privilegios de ADMINISTRADOR, DUENO o superusuario.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Debes iniciar sesión para acceder a esta sección.')
                return redirect('login')

            if not getattr(request.user, 'es_administrador', False):
                messages.error(request, 'No tienes permisos de administración para realizar esta acción.')
                return redirect(login_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def dueno_required(login_url='dashboard'):
    """
    Decorador para restringir el acceso a vistas gerenciales exclusivas del DUEÑO.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.warning(request, 'Debes iniciar sesión para acceder a esta sección.')
                return redirect('login')

            if not getattr(request.user, 'es_dueno', False):
                messages.error(request, 'Esta sección está reservada exclusivamente para la gerencia.')
                return redirect(login_url)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator