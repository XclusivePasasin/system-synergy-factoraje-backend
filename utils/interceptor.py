from flask import request, jsonify
from functools import wraps
from services.usuario_service import UsuarioService  
from utils.response import response_error
from utils.destructor import is_token_blacklisted

def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Intentar obtener el token desde los encabezados de la solicitud
        try:
            # Buscar el encabezado 'Authorization'
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return response_error("Cabecera de autorización no encontrada", http_status=401)

            # Validar el formato del token (debe empezar con 'Bearer')
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
            else:
                return response_error("El formato del token es incorrecto", http_status=401)
        except Exception as e:
            return response_error(f"Error al procesar la cabecera de autorización: {str(e)}", http_status=401)

        # Verificar si el token está en la lista negra
        if is_token_blacklisted(token):
            return response_error("Token inválido o revocado", http_status=401)

        # Validar el token utilizando el servicio
        resultado_validacion = UsuarioService.validar_token(token)
        if resultado_validacion == 'invalido':
            return response_error("Token de autorización inválido", http_status=401)
        elif resultado_validacion == 'vencido':
            return response_error("Token de autorización vencido", http_status=401)

        # Token válido, proceder a ejecutar la función protegida
        return f(*args, **kwargs)

    return decorated_function