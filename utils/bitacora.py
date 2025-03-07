from functools import wraps
from flask import request
from datetime import datetime
from utils.db import db
from models.bitacoras import Bitacora
from models.usuarios import Usuario
from utils.response import response_error  

def bitacora(modulo, accion):
    """ Decorador para registrar automáticamente eventos en la bitácora con verificación de usuario e ID afectado. """
    def decorador(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            id_usuario = request.headers.get("id_usuario_bitacora")
            usuario = request.headers.get("nombre_usuario_bitacora")

            # Validamos que la informacion de autenticación esté presente
            if not id_usuario:
                return response_error("Falta el id de usuario, necesario para registrar la bitácora.", http_status=401)
            if not usuario:
                return response_error("Falta el nombre de usuario, necesario para registrar la bitácora.", http_status=401)

            try:
                id_usuario = int(id_usuario)  # Convertir a número el id de usuario
            except ValueError:
                return response_error("El ID de usuario debe ser un número válido.", http_status=400)

            # Verificar si el usuario existe en la base de datos y está activo
            usuario_db = Usuario.query.filter_by(id=id_usuario, activo=True, reg_activo=True).first()
            if not usuario_db:
                return response_error("El usuario no existe o está inactivo.", http_status=403)

            #  Obtener el registro afectado de la solicitud
            registro_afectado = None

            # 1️⃣ Si el ID viene en los headers
            if request.headers.get("id"):
                registro_afectado = request.headers.get("id")

            # 2️⃣ Si el ID viene en la URL (GET, DELETE)
            if request.args.get("id"):
                registro_afectado = request.args.get("id")

            # 3️⃣ Si el ID viene en el JSON del body (POST, PUT, PATCH)
            try:
                data = request.get_json()
                if isinstance(data, dict) and "id" in data:
                    registro_afectado = data["id"]
            except Exception:
                pass  # Si hay un error en el JSON, se ignora

            # Si no se encontró el ID, devolver error
            if not registro_afectado:
                return response_error("Falta el ID del registro afectado.", http_status=400)

            # Generar el detalle con el ID extraído
            detalle = f"Acción: {accion} - Endpoint: {request.path} - Método: {request.method} - Identificacion Registro afectado: {registro_afectado}"

            try:
                respuesta = f(*args, **kwargs)  # Ejecutar la función original
                
                # Registrar éxito en bitácora
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
                # Registrar error en bitácora pero sin interferir con la respuesta
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
