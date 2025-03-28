from functools import wraps
from flask import request
from datetime import datetime
from utils.db import db
from models.bitacoras import Bitacora
from models.usuarios import Usuario
from utils.response import response_error  

def bitacora(modulo, accion):
    """ Decorador para registrar automáticamente eventos en la bitácora usando datos del cuerpo del request. """
    def decorador(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Leer JSON del body
            try:
                data = request.get_json()
            except Exception:
                return response_error("Error al leer el cuerpo de la solicitud (JSON inválido).", http_status=400)

            if not isinstance(data, dict):
                return response_error("El cuerpo de la solicitud debe ser un objeto JSON válido.", http_status=400)

            # Obtener datos del body
            id_usuario = data.get("id_usuario_bitacora")
            usuario = data.get("nombre_usuario_bitacora")
            registro_afectado = data.get("id_aprobador")  # Este será el ID del registro afectado

            # Validar campos requeridos
            if not id_usuario:
                return response_error("Falta el id de usuario, necesario para registrar la bitácora.", http_status=401)
            if not usuario:
                return response_error("Falta el nombre de usuario, necesario para registrar la bitácora.", http_status=401)
            if not registro_afectado:
                return response_error("Falta el ID del registro afectado (id_aprobador).", http_status=400)

            try:
                id_usuario = int(id_usuario)
            except ValueError:
                return response_error("El ID de usuario debe ser un número válido.", http_status=400)

            # Verificar existencia del usuario
            usuario_db = Usuario.query.filter_by(id=id_usuario, activo=True, reg_activo=True).first()
            if not usuario_db:
                return response_error("El usuario no existe o está inactivo.", http_status=403)

            # Detalle del evento
            detalle = (
                f"Acción: {accion} - Endpoint: {request.path} - Método: {request.method} "
                f"- ID Registro afectado (id_aprobador): {registro_afectado}"
            )

            try:
                respuesta = f(*args, **kwargs)

                nueva_bitacora = Bitacora(
                    usuario=usuario,
                    id_usuario=id_usuario,
                    modulo=modulo,
                    accion=accion,
                    detalle=detalle,
                    exito=True,
                    tipo="INFO",
                    fecha=datetime.utcnow()
                )
            except Exception as e:
                detalle_error = f"Error en {accion}: {str(e)}"
                nueva_bitacora = Bitacora(
                    usuario=usuario,
                    id_usuario=id_usuario,
                    modulo=modulo,
                    accion=f"Error en {accion}",
                    detalle=detalle_error,
                    exito=False,
                    tipo="ERROR",
                    fecha=datetime.utcnow()
                )
                db.session.add(nueva_bitacora)
                db.session.commit()
                raise

            db.session.add(nueva_bitacora)
            db.session.commit()

            return respuesta

        return wrapper
    return decorador