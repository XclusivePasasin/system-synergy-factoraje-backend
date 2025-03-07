from utils.db import db
from models.permisos import Permiso
from models.roles import Rol
from models.menus import Menu
from models.usuarios import Usuario
from flask import request
from utils.response import response_success, response_error

class PermisosService:
    @staticmethod
    def actualizar_permisos(data):
        id_rol = data.get('id_rol')
        nombre = data.get('nombre')
        descripcion = data.get('descripcion')
        menus = data.get('menus')  

        # Validar que los menús estén presentes en el payload
        if not menus:
            return response_error("No se proporcionaron menús.", http_status=400)

        try:
            # Si el id_rol es None, se crea un nuevo rol
            if id_rol is None:
                if not nombre:
                    return response_error("El nombre del rol es obligatorio para crear un nuevo rol.", http_status=400)

                nuevo_rol = Rol(rol=nombre, nombre=nombre, descripcion=descripcion)
                db.session.add(nuevo_rol)
                db.session.commit()
                id_rol = nuevo_rol.id  
                rol = nuevo_rol
            else:
                # Validar si el rol existe
                rol = Rol.query.get(id_rol)
                if not rol:
                    return response_error("ID de rol no válido.", http_status=400)

                # Actualizar el nombre y la descripción si se proporcionan
                if nombre:
                    rol.nombre = nombre
                    rol.rol = nombre  
                if descripcion is not None:
                    rol.descripcion = descripcion

                db.session.commit()  # Guardar los cambios en el rol

            # Eliminar permisos existentes para el rol especificado
            Permiso.query.filter_by(id_rol=id_rol).delete()
            db.session.commit()

            # Insertar nuevos permisos (menús)
            nuevos_permisos = []
            for id_menu in menus:
                nuevo_permiso = Permiso(
                    id_rol=id_rol,
                    id_menu=id_menu
                )
                nuevos_permisos.append(nuevo_permiso)

            db.session.add_all(nuevos_permisos)
            db.session.commit()

            return response_success(f"Permisos asignados exitosamente para el rol '{rol.nombre}'.", "Permisos asignados exitosamente.")

        except Exception as e:
            db.session.rollback()
            return response_error(f"Ocurrió un error: {str(e)}", http_status=500)



    @staticmethod
    def obtener_permisos_por_rol(id_rol):
        # Validar si el rol existe
        rol = Rol.query.get(id_rol)
        if not rol:
            return response_error("ID de rol no válido.", http_status=400)

      # Obtener todos los permisos asociados a ese rol
        permisos = Permiso.query.filter_by(id_rol=id_rol).all()

        # Lista de nombres de los campos de permisos a incluir
        # campos_permisos = [
        #     "create_perm", "edit_perm", "delete_perm", "view_perm",
        #     "approve_deny", "download", "process",
        #     "edit_user", "create_user", "active_inactive_user",
        #     "edit_role", "create_role"
        # ]

        # # Construir la lista de permisos filtrando dinámicamente los campos no nulos y convirtiendo a 1 o 0
        permisos_list = [
            {
                "id_menu": permiso.id_menu
            }
            for permiso in permisos
        ]
        # Construir el payload de respuesta
        response_data = {
                "id_rol": rol.id,
                "nombre": rol.nombre,
                "descripcion": rol.descripcion,
                "permisos": permisos_list
        }

        return response_success(response_data, "Permisos obtenidos exitosamente.")

    @staticmethod
    def obtener_todos_los_roles():
        # Obtener todos los roles de la base de datos
        roles = Rol.query.filter(Rol.id != 5).all()

        if not roles:
            return response_error("No se encontraron roles.", http_status=404)

        # Construir la lista de roles con sus permisos
        roles_list = [
            {
                "id_rol": rol.id,
                "nombre": rol.nombre,
                "descripcion": rol.descripcion,
            }
            for rol in roles
        ]

        response_data = {
                "roles": roles_list
        }

        return response_success(response_data, "Roles obtenidos exitosamente.")
    
    @staticmethod
    def eliminar_rol(rol_id):
        """
        Endpoint para eliminar un rol.
        Recibe el rol_id como query parameter.
        """
        try:
            rol_id = request.args.get('rol_id', type=int)
            if not rol_id:
                return response_error("El parámetro 'rol_id' es obligatorio y debe ser un entero válido.", http_status=400)

            # Lista de roles que no se pueden eliminar
            roles_protegidos = ["Administrador", "Operador de ICC", "Operador de Synergy", "Auditor"]

            # Buscar el rol en la base de datos
            rol = Rol.query.get(rol_id)
            if not rol:
                return response_error("El rol especificado no existe.", http_status=404)

            if rol.nombre in roles_protegidos:
                return response_error(
                    f"El rol '{rol.nombre}' no se puede eliminar porque es un rol predeterminado.",
                    http_status=400
                )

            # Verificar si existen usuarios asociados con el rol
            usuarios_asociados = Usuario.query.filter_by(id_rol=rol_id).count()

            if usuarios_asociados > 0:
                return response_error(
                    "No se puede eliminar el rol porque hay usuarios asociados a este rol.",
                    http_status=400
                )

            # Eliminar el rol
            db.session.delete(rol)
            db.session.commit()

            return response_success(None, "Rol eliminado exitosamente.")

        except Exception as e:
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)



    @staticmethod
    def obtener_todos_menus():
        try:
            # Obtener todos los menús
            menus = Menu.query.all()

            # Construir una lista de diccionarios con los datos de los menús
            menus_list = [
                {
                    "id": menu.id,
                    "menu": menu.menu,
                    "description": menu.description,
                    "path": menu.path,
                    "icon": menu.icon,
                    "orden": menu.orden,
                    "padre": menu.padre,
                    "created_at": menu.created_at.strftime("%Y-%m-%d %H:%M:%S") if menu.created_at else None,
                    "updated_at": menu.updated_at.strftime("%Y-%m-%d %H:%M:%S") if menu.updated_at else None
                }
                for menu in menus
            ]

            response_data = {
                "menus": menus_list
            }

            return response_success(response_data, "Menús obtenidos exitosamente.")

        except Exception as e:
            return response_error(f"Ocurrió un error al obtener los menús: {str(e)}", http_status=500)