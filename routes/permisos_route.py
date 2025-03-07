from flask import Blueprint, request
from models.permisos import Permiso
from models.menus import Menu
from models.roles import Rol
from utils.response import response_success, response_error
from utils.interceptor import token_required
from services.permisos_service import PermisosService

permisos_bp = Blueprint('permiso', __name__)

# endpoint for actualizar permisos
@permisos_bp.route('/actualizar-permisos', methods=['PUT'])
@token_required
def actualizar_permisos():
    try:
        data = request.get_json()
        if not data:
            return response_error("Datos no proporcionados", http_status=400)

        if 'id_rol' not in data or 'menus' not in data:
            return response_error("El payload debe contener 'id_rol' y 'menus'.", http_status=400)

        return PermisosService.actualizar_permisos(data)

    except KeyError as e:
        return response_error(f"Falta una clave en el payload: {str(e)}", http_status=400)

    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

@permisos_bp.route('/listar-permisos', methods=['GET'])
@token_required
def listar_permisos():
    try:
        id_rol = request.args.get('id_rol', type=int)
        if id_rol is None:
            return response_error("El parámetro 'id_rol' es obligatorio.", http_status=400)

        return PermisosService.obtener_permisos_por_rol(id_rol)

    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

@permisos_bp.route('/listar-menus', methods=['GET'])
@token_required
def listar_menus():
    try:
        return PermisosService.obtener_todos_menus()

    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500) 

@permisos_bp.route('/listar-roles', methods=['GET'])
@token_required
def listar_roles():
    try:
        return PermisosService.obtener_todos_los_roles()

    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)   

@permisos_bp.route('/eliminar-rol', methods=['DELETE'])
@token_required
def eliminar_rol():
    try:
        rol_id = request.args.get('rol_id', type=int)
        if not rol_id:
            return response_error("El parámetro 'rol_id' es obligatorio y debe ser un entero válido.", http_status=400)
        
        return PermisosService.eliminar_rol(rol_id)

    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)        