from flask import Blueprint, request
from services.usuario_service import UsuarioService
from models.usuarios import Usuario
from utils.interceptor import token_required
from utils.response import response_success, response_error

usuarios_bp = Blueprint('usuario', __name__)

@usuarios_bp.route('/crear-usuario', methods=['POST'])  
def crear_usuario():
    """
    Endpoint para crear un usuario.
    """
    try:
        data = request.get_json()
        if not data:
            return response_error("Datos no proporcionados", http_status=400)
        return UsuarioService.crear_usuario(data)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

@usuarios_bp.route('/inicio-sesion', methods=['POST'])
def inicio_sesion():
    """
    Endpoint para iniciar sesión.
    """
    try:
        data = request.get_json()
        if not data:
            return response_error("Datos no proporcionados", http_status=400)
        return UsuarioService.inicio_sesion(data)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

@usuarios_bp.route('/token', methods=['POST'])
def cargar_token():
    """
    Endpoint para generar un nuevo token.
    """
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return response_error("El campo 'email' es obligatorio", http_status=400)
        return UsuarioService.cargar_token(data)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

@usuarios_bp.route('/cerrar-sesion', methods=['POST'])
@token_required  
def cerrar_sesion():
    """
    Endpoint para cerrar sesión y destruir el token del usuario.
    """
    try:
        # Obtener el ID del usuario desde los query parameters
        usuario_id = request.args.get("usuario_id", type=int)
        if not usuario_id:
            return response_error("El parámetro 'usuario_id' es obligatorio", http_status=400)

        # Obtener el token del encabezado Authorization
        token = request.headers.get('Authorization').split('Bearer ')[-1]

        # Llamar al servicio para destruir el token
        return UsuarioService.destruir_token(usuario_id, token)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    
@usuarios_bp.route('/cambiar-contraseña', methods=['POST'])
@token_required
def actualizacion_contrasena_inicio_sesion():
    """
    Endpoint para la primera actualización de contraseña al inicio de sesión.
    """
    try:
        data = request.get_json()
        if not data or 'email' not in data or 'nueva_contrasena' not in data:
            return response_error("Los campos 'email' y 'nueva_contrasena' son obligatorios", http_status=400)
        email = data['email']
        nueva_contrasena = data['nueva_contrasena']
        
        # Llamada al servicio para actualizar la contraseña
        return UsuarioService.actualizar_contraseña(email, nueva_contrasena)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    

@usuarios_bp.route('/actualizar-usuario', methods=['PUT'])
@token_required
def actualizar_usuario_route():
    """
    Endpoint para actualizar la información de un usuario excepto el correo electrónico.
    Utiliza el usuario_id como query parameter para identificar al usuario a actualizar.
    """
    usuario_id = request.args.get('usuario_id', type=int)  
    if not usuario_id:
        return response_error("usuario_id es requerido", http_status=400)

    try:
        data = request.get_json()
        if not data:
            return response_error("Datos no proporcionados", http_status=400)

        return UsuarioService.actualizar_usuario(usuario_id, data)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    
@usuarios_bp.route('/cambiar-estado-usuario', methods=['POST'])
@token_required
def cambiar_estado_usuario_route():
    """
    Endpoint para activar o desactivar un usuario.
    Recibe el usuario_id y el nuevo estado activo en el cuerpo de la solicitud.
    """
    try:
        data = request.get_json()
        if not data:
            return response_error("Datos no proporcionados", http_status=400)
        
        # Validación de los datos recibidos
        usuario_id = data.get('usuario_id')
        activo = data.get('activo')

        if usuario_id is None:
            return response_error("El 'usuario_id' es requerido", http_status=400)
        if activo is None:
            return response_error("El estado 'activo' es requerido", http_status=400)

        # Llamada al servicio para actualizar el estado activo del usuario
        return UsuarioService.cambiar_estado_usuario(usuario_id, activo)

    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    
@usuarios_bp.route('/listar-usuarios', methods=['GET'])
@token_required
def listar_usuarios():
    """
    Endpoint para listar todos los usuarios que no han sido eliminados.
    Incluye filtros opcionales y paginación.
    """
    try:
        # Obtener parámetros de consulta para la paginación y filtros
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        nombres = request.args.get('nombre', '')
        apellidos = request.args.get('apellido', '')
        email = request.args.get('email', '')
        cargo = request.args.get('cargo', '')

        # Construir el query base
        query = Usuario.query.filter(Usuario.reg_activo == True, Usuario.id != 4)  # Excluir el usuario con id = 4 (solicitador)

        # Aplicar filtros si se proporcionan
        if nombres:
            query = query.filter(Usuario.nombres.ilike(f"%{nombres}%"))
        if apellidos:
            query = query.filter(Usuario.apellidos.ilike(f"%{apellidos}%"))
        if email:
            query = query.filter(Usuario.email.ilike(f"%{email}%"))
        if cargo:
            query = query.filter(Usuario.cargo.ilike(f"%{cargo}%"))


        # Paginación y conteo total después de filtrar
        total_usuarios = query.count()
        usuarios = query.offset((page - 1) * per_page).limit(per_page).all()

        # Construir la respuesta con los usuarios
        response_data = {
            "current_page": page,
            "per_page": per_page,
            "total_pages": (total_usuarios + per_page - 1) // per_page,
            "usuarios": [
                {
                    "id": usuario.id,
                    "nombres": usuario.nombres,
                    "apellidos": usuario.apellidos,
                    "email": usuario.email,
                    "cargo": usuario.rol.nombre,
                    "activo": usuario.activo,
                    "id_rol": usuario.id_rol,
                    "created_at": usuario.created_at.isoformat(),
                    "updated_at": usuario.updated_at.isoformat(),
                    "reg_activo": usuario.reg_activo,
                }
                for usuario in usuarios
            ]
        }

        return response_success(response_data, "Lista de usuarios obtenida exitosamente")
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    
@usuarios_bp.route('/detalle-usuario', methods=['GET'])
@token_required
def detalle_usuario():
    """
    Endpoint para obtener el detalle de un usuario específico.
    El usuario_id se recibe como query parameter.
    """
    usuario_id = request.args.get('usuario_id', type=int)
    if not usuario_id:
        return response_error("El parámetro 'usuario_id' es obligatorio y debe ser un número válido.", http_status=400)

    try:
        usuario = Usuario.query.filter_by(id=usuario_id, reg_activo=True).first()
        if not usuario:
            return response_error("Usuario no encontrado", http_status=404)

        usuario_data = {
            "id": usuario.id,
            "nombres": usuario.nombres,
            "apellidos": usuario.apellidos,
            "email": usuario.email,
            "cargo": usuario.cargo,
            "id_rol": usuario.id_rol,
            "created_at": usuario.created_at,
            "updated_at": usuario.updated_at,
            "activo": 1 if usuario.activo else 0,
            "reg_activo": 1 if usuario.reg_activo else 0,
        }
        return response_success(usuario_data, "Detalle del usuario obtenido exitosamente", http_status=200)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    

@usuarios_bp.route('/eliminar-usuario', methods=['DELETE'])
@token_required
def eliminar_usuario_route():
    """
    Endpoint para "eliminar" lógicamente un usuario.
    Recibe el usuario_id como query parameter.
    """
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        if not usuario_id:
            return response_error("El parámetro 'usuario_id' es obligatorio y debe ser un entero válido.", http_status=400)

        return UsuarioService.eliminar_usuario(usuario_id)

    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    
@usuarios_bp.route('/restablecer-contraseña', methods=['POST'])
@token_required
def restablecer_contraseña():
    """
    Endpoint para restablecer la contraseña de un usuario obteniendo el id del usuario como query parameter.
    """
    try:
        usuario_id = request.args.get('usuario_id', type=int)
        if not usuario_id:
            return response_error("El parámetro 'usuario_id' es obligatorio y debe ser un número entero.", http_status=400)
        
        # Llamada al servicio para restablecer la contraseña
        return UsuarioService.restablecer_contraseña(usuario_id)
    except Exception as e:
        return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

   


