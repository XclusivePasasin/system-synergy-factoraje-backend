from datetime import datetime, timedelta
import hashlib
import re
from flask import current_app
import jwt
from models.usuarios import Usuario
from models.permisos import Permiso
from models.menus import Menu
from models.roles import Rol
from models.parametros import Parametro
from utils.db import db
from utils.response import response_success, response_error
from sqlalchemy.exc import SQLAlchemyError
from utils.destructor import blacklist_token
from services.email_service import *

class UsuarioService:
    @staticmethod
    def crear_usuario(data):
        try:
            # Validar los campos requeridos
            campos_requeridos = ['nombres', 'apellidos', 'email', 'id_rol']
            for campo in campos_requeridos:
                if campo not in data:
                    return response_error(f"El campo {campo} es obligatorio", http_status=400)

            nombres = data['nombres']
            apellidos = data['apellidos']
            email = data['email']
            id_rol = data['id_rol']

            if len(nombres) < 2 or len(nombres) > 50 or len(apellidos) < 2 or len(apellidos) > 50:
                return response_error("El formato o longitud del nombre o apellidos no es válido", http_status=400)

            # Validar longitud y formato del correo electrónico
            if len(email) < 10 or len(email) > 100 or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return response_error("El formato o longitud del correo electrónico no es válido", http_status=400)

            # Validar que el rol existe
            rol = Rol.query.get(id_rol)
            if not rol:
                return response_error("El rol especificado no existe", http_status=404)

            # Asignar el cargo basado en el nombre del rol
            cargo = rol.rol

            # Validar que el correo no esté registrado
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                return response_error("El correo ya está registrado", http_status=409)

            # Generar contraseña temporal
            # temp_password = UsuarioService.generar_contraseña_temp()
            temp_password = '12345678'
            print('temp_password: ', temp_password)

            # Hashear la contraseña temporal usando hashlib con SHA-256
            salt = current_app.config['SALT_SECRET']
            hashed_temp_password = hashlib.sha256((temp_password + salt).encode('utf-8')).hexdigest()

            # Crear el nuevo usuario
            nuevo_usuario = Usuario(
                nombres=nombres,
                apellidos=apellidos,
                email=email,
                temp_password=hashed_temp_password,
                cargo=cargo,
                id_rol=id_rol
            )

            # Guardar en la base de datos
            db.session.add(nuevo_usuario)
            db.session.commit()

            # Obtener el valor de la clave NOM-EMPRESA
            parametro_nombre_empresa = Parametro.query.filter_by(clave='NOM-EMPRESA').first()
            if not parametro_nombre_empresa:
                return response_error("No se encontró el parámetro NOM-EMPRESA", http_status=500)

            nombre_empresa = parametro_nombre_empresa.valor

            # Enviar correo con las credenciales al usuario
            datos_credenciales = {
                "nombreUsuario": f"{nombres} {apellidos}",
                "correoElectronico": email,
                "contrasenaTemporal": temp_password,
                "nombreEmpresa": nombre_empresa,
            }
            asunto = "Credenciales de acceso al sistema de pronto pago"
            contenido_html_credenciales = generar_plantilla('correo_contraseña_temporal.html', datos_credenciales)
            # Enviar el correo
            enviar_correo(email, asunto, contenido_html_credenciales)

            respuesta = {
                "usuario_id": nuevo_usuario.id,
                "nombres": nuevo_usuario.nombres,
                "apellidos": nuevo_usuario.apellidos,
                "email": nuevo_usuario.email,
                "cargo": nuevo_usuario.cargo,
                "id_rol": nuevo_usuario.id_rol
            }
            return response_success(respuesta, "Usuario creado exitosamente. Las credenciales han sido enviadas al correo registrado.", http_status=201)

        except Exception as e:
            db.session.rollback()
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)


        
    @staticmethod
    def inicio_sesion(data):
        """
        Autentica un usuario utilizando el email y la contraseña, y genera un JWT definitivo.
        """
        try:
            # Validar los campos requeridos
            if 'email' not in data or 'password' not in data:
                return response_error("Los campos 'email' y 'password' son obligatorios", http_status=400)

            email = data['email']
            password = data['password']

            # Validar formato del email
            if len(email) < 10 or len(email) > 100 or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return response_error("El formato o longitud del correo electrónico no es válido", http_status=400)

            # Buscar al usuario en la base de datos por email
            usuario_encontrado = Usuario.query.filter_by(email=email).first()
            if not usuario_encontrado:
                return response_error("El usuario no existe", http_status=401)
            
            # Verificar si el usuario está marcado como inactivo
            if not usuario_encontrado.activo:
                return response_error("Este usuario está inactivo", http_status=403)  
            
            if not usuario_encontrado.reg_activo:
                return response_error("Este usuario ha sido eliminado del sistema", http_status=403)  

            # Generar el hash de la contraseña ingresada
            salt = current_app.config.get('SALT_SECRET')
            hashed_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()

            # Verificar si el usuario tiene una contraseña o solo la contraseña temporal
            if usuario_encontrado.password:
                # Si el usuario tiene una contraseña (es decir, ya la ha cambiado anteriormente)
                if hashed_password != usuario_encontrado.password:
                    return response_error("La contraseña es incorrecta", http_status=401)
                change_password = 0
            else:
                # Si el campo 'password' está vacío, se verifica contra la 'temp_password'
                hashed_temp_password = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
                if hashed_temp_password != usuario_encontrado.temp_password:
                    return response_error("La contraseña es incorrecta", http_status=401)
                change_password = 1 

            # Consultar el rol del usuario y los permisos asociados
            rol = Rol.query.get(usuario_encontrado.id_rol)
            permisos = Permiso.query.filter_by(id_rol=usuario_encontrado.id_rol).all()

            # Construir la estructura de permisos y menús
            permisos_data = []
            for permiso in permisos:
                menu = Menu.query.get(permiso.id_menu)
                permisos_data.append({ 
                    "menu": {
                        "id": menu.id,
                        "menu": menu.menu,
                        "descripcion": menu.description,
                        "path": menu.path,
                        "icon": menu.icon,
                        "orden": menu.orden,
                        "padre": menu.padre
                    }
                })

            # Crear el token JWT
            expires_in = 86400  # 24 horas
            access_token = UsuarioService.crear_token(email)
            token = access_token["token"]

            if not access_token:
                return response_error("Error al generar el token", http_status=500)

            # Construir la respuesta con los datos del usuario y el token
            usuario_data = {
                "id": usuario_encontrado.id,
                "nombres": usuario_encontrado.nombres,
                "apellidos": usuario_encontrado.apellidos,
                "email": usuario_encontrado.email,
                "role": rol.rol if rol else "Sin rol asignado",
                "id_role": rol.id if rol else "Sin id rol asignado",
                "permissions": permisos_data, 
            }

            # Responder con la estructura correcta
            respuesta = {
                "usuario": usuario_data,
                "access_token": token,  
                "expires_in": expires_in,
                "change_password": change_password 
            }

            return response_success(respuesta, "Autenticación completada", http_status=200)
        except Exception as e:
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)


    @staticmethod
    def generar_contraseña_temp(length=10):
        import string
        import random
        caracteres = string.ascii_letters + string.digits
        return ''.join(random.choice(caracteres) for _ in range(length))

    @staticmethod
    def crear_token(email):
        """
        Crea un token JWT con una validez de 24 horas y lo guarda en el usuario.
        """
        try:
            # Obtener clave secreta desde configuración
            secret_key = current_app.config.get('SECRET_KEY')
            expiration = datetime.utcnow() + timedelta(hours=24)

            payload = {
                'email': email,  
                'exp': expiration
            }

            # Generar el token JWT
            token = jwt.encode(payload, secret_key, algorithm='HS256')

            # Actualizar el token en la base de datos
            usuario_encontrado = Usuario.query.filter_by(email=email).first()  
            if not usuario_encontrado:
                return None  

            usuario_encontrado.token = token
            usuario_encontrado.token_date_end = expiration

            db.session.commit()

            return {
                "usuario_id": usuario_encontrado.id,
                "nombres": usuario_encontrado.nombres,
                "apellidos": usuario_encontrado.apellidos,
                "email": usuario_encontrado.email,
                "token": token
            }
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Error al crear el token: {str(e)}")
    
    @staticmethod
    def cargar_token(data):
        """
        Genera un nuevo token para un usuario existente basado en su email.
        """
        try:
            # Validar que se haya proporcionado el email
            if 'email' not in data:
                return response_error("El campo 'email' es obligatorio", http_status=400)

            email = data['email']

            # Validar longitud y formato del email
            if len(email) < 10 or len(email) > 100 or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return response_error("El formato o longitud del correo electrónico no es válido", http_status=400)

            # Buscar al usuario en la base de datos por email
            usuario_encontrado = Usuario.query.filter_by(email=email).first()
            if not usuario_encontrado:
                return response_error("El usuario no existe", http_status=404)

            # Generar un nuevo token JWT
            expires_in = 86400  # 24 horas
            access_token = UsuarioService.crear_token(email)
            token = access_token["token"]

            if not access_token:
                return response_error("Error al generar el token", http_status=500)

            # Consultar el rol del usuario y los permisos asociados
            rol = Rol.query.get(usuario_encontrado.id_rol)
            permisos = Permiso.query.filter_by(id_rol=usuario_encontrado.id_rol).all()

            # Construir la estructura de permisos y menús
            permisos_data = []
            for permiso in permisos:
                menu = Menu.query.get(permiso.id_menu)
                permisos_data.append({
                    "create_perm": 1 if permiso.create_perm else 0, 
                    "edit_perm": 1 if permiso.edit_perm else 0,     
                    "delete_perm": 1 if permiso.delete_perm else 0,  
                    "view_perm": 1 if permiso.view_perm else 0,      
                    "menu": {
                        "id": menu.id,
                        "menu": menu.menu,
                        "path": menu.path,
                        "icon": menu.icon,
                        "orden": menu.orden,
                        "padre": menu.padre
                    }
                })

            # Construir los datos del usuario
            usuario_data = {
                "id": usuario_encontrado.id,
                "nombres": usuario_encontrado.nombres,
                "apellidos": usuario_encontrado.apellidos,
                "email": usuario_encontrado.email,
                "role": rol.rol if rol else "Sin rol asignado",
                "permissions": permisos_data
            }

            # Construir la respuesta con los mismos campos que inicio_sesion
            respuesta = {
                "usuario": usuario_data,
                "access_token": token,  
                "expires_in": expires_in
            }

            return response_success(respuesta, "Token generado exitosamente", http_status=200)
        except Exception as e:
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)



        
    @staticmethod
    def validar_token(token):
        """
        Valida la vigencia del token JWT.
        :param token: El token de sesión.
        :return: 'valido' si el token es válido, 'vencido' si ha expirado, 'invalido' si es inválido.
        """
        try:
            # Obtener la clave secreta desde la configuración
            secret_key = current_app.config.get('SECRET_KEY')
            # Decodificar el token JWT
            jwt.decode(token, secret_key, algorithms=['HS256'])
            # Si no se lanza una excepción, el token es válido
            return 'valido'
        except jwt.ExpiredSignatureError:
            # El token ha expirado
            return 'vencido'
        except jwt.InvalidTokenError:
            # El token es inválido
            return 'invalido'
        
    @staticmethod
    def destruir_token(usuario_id, token):
        """
        Elimina el token y su fecha de expiración del usuario, y agrega el token a la lista negra.
        """
        try:
            # Buscar el usuario por ID
            usuario = db.session.query(Usuario).filter_by(id=usuario_id).first()
            if not usuario:
                return response_error("Usuario no encontrado", http_status=404)

            # Validar que el token pertenece al usuario
            if usuario.token != token:
                return response_error("El token proporcionado no corresponde al usuario", http_status=403)

            # Agregar el token a la lista negra
            blacklist_token(token)

            # Eliminar el token y la fecha de expiración de la base de datos
            usuario.token = None
            usuario.token_date_end = None
            db.session.commit()

            return response_success(None, "Token destruido exitosamente")
        except Exception as e:
            db.session.rollback()
            return response_error(f"Error al destruir el token: {str(e)}", http_status=500)
        
    @staticmethod
    def actualizar_contraseña(email, nueva_contraseña):
        """
        Actualiza la contraseña principal para el usuario especificado, solo si la contraseña temporal no es None.
        Si la contraseña temporal es None, retorna un error indicando que no se puede actualizar la contraseña.
        """
        try:
            # Buscar al usuario en la base de datos por email
            usuario = Usuario.query.filter_by(email=email).first()
            if not usuario:
                return response_error("El usuario no existe", http_status=404)

            # Verificar si la contraseña temporal está presente
            if usuario.temp_password is None:
                return response_error("Actualización de contraseña no permitida sin una contraseña temporal válida", http_status=403)

            # Hashear la nueva contraseña
            salt = current_app.config['SALT_SECRET']
            hashed_password = hashlib.sha256((nueva_contraseña + salt).encode('utf-8')).hexdigest()

            # Actualizar la contraseña del usuario en la base de datos y limpiar la contraseña temporal
            usuario.password = hashed_password
            usuario.temp_password = None  # Establecer la contraseña temporal a None
            db.session.commit()

            # Retornar el email con un mensaje de éxito
            respuesta = {
                "email": email,
                "mensaje": "Contraseña actualizada exitosamente"
            }

            return response_success(respuesta, "Contraseña actualizada correctamente", http_status=200)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

    @staticmethod
    def actualizar_usuario(usuario_id, data):
        """
        Actualiza la información de un usuario, incluyendo el correo electrónico si se proporciona.
        """
        try:
            # Buscar al usuario por su ID
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return response_error("Usuario no encontrado", http_status=404)

            # Actualizar nombres
            if 'nombres' in data and data['nombres'].strip():
                usuario.nombres = data['nombres'].strip()
            else:
                return response_error("El campo 'nombres' está vacío o no es válido", http_status=400)

            # Actualizar apellidos
            if 'apellidos' in data and data['apellidos'].strip():
                usuario.apellidos = data['apellidos'].strip()
            else:
                return response_error("El campo 'apellidos' está vacío o no es válido", http_status=400)

            # Actualizar rol y cargo basado en el rol
            if 'id_rol' in data and data['id_rol']:
                rol = Rol.query.get(data['id_rol'])
                if not rol:
                    return response_error("Rol no encontrado", http_status=404)
                usuario.id_rol = data['id_rol']
                usuario.cargo = rol.nombre  # Asignar cargo basado en el nombre del rol
            else:
                return response_error("El campo 'id_rol' está vacío o no es válido", http_status=400)

            # Actualización de la contraseña si se proporciona
            if 'password' in data:
                if data['password'] and len(data['password']) >= 8:
                    salt = current_app.config['SALT_SECRET']
                    hashed_password = hashlib.sha256((data['password'] + salt).encode('utf-8')).hexdigest()
                    usuario.password = hashed_password
                elif data['password']:
                    return response_error("La contraseña debe tener al menos 8 caracteres.", http_status=400)

            # Actualizar correo electrónico si se proporciona y es diferente al actual
            if 'email' in data and data['email'].strip():
                nuevo_email = data['email'].strip()
                if nuevo_email != usuario.email:
                    # Verificar si el nuevo correo ya está en uso por otro usuario
                    if Usuario.query.filter_by(email=nuevo_email).first():
                        return response_error("El correo electrónico ya está en uso", http_status=400)
                    usuario.email = nuevo_email
            # Si no se proporciona un correo electrónico, no se actualiza y no se devuelve un error

            # Guardar los cambios en la base de datos
            db.session.commit()
            return response_success({"mensaje": "Usuario actualizado exitosamente"}, http_status=200)

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

    
    @staticmethod
    def cambiar_estado_usuario(usuario_id, activo):
        try:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return response_error("Usuario no encontrado", http_status=404)
            # Validación para evitar modificar el estado de un usuario con id_rol = 1
            if usuario.id_rol == 1:
                return response_error("No se puede modificar el estado de un usuario administrador.", http_status=403)
            
            # Actualizar el estado activo
            usuario.activo = activo
            db.session.commit()
            return response_success({"mensaje": f"Estado del usuario {'activado' if activo else 'desactivado'} exitosamente"}, http_status=200)
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
    
    @staticmethod
    def eliminar_usuario(usuario_id):
        try:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return response_error("Usuario no encontrado", http_status=404)

            # Validación para evitar eliminar un usuario con id_rol = 1 (Administrador)
            if usuario.id_rol == 1:
                return response_error("No se puede eliminar a un usuario administrador.", http_status=403)

            usuario.reg_activo = False
            db.session.commit()
            return response_success({"mensaje": "Usuario eliminado exitosamente"}, http_status=200)

        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)

        
    @staticmethod
    def restablecer_contraseña(usuario_id):
        try:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return response_error("Usuario no encontrado", http_status=404)

            # Comprobar si el usuario está activo y no eliminado
            if not usuario.activo or not usuario.reg_activo:
                return response_error("No se puede restablecer la contraseña: el usuario está inactivo o eliminado", http_status=403)
            
            # Verificar si ya se ha restablecido la contraseña y el usuario aún no ha establecido una nueva
            if usuario.password is None:
                return response_error("Debes iniciar sesión y establecer una nueva contraseña antes de poder restablecerla nuevamente.", http_status=403)

            # Generar una nueva contraseña temporal
            temp_password = UsuarioService.generar_contraseña_temp()

            # Hashear la contraseña temporal para guardarla de forma segura
            salt = current_app.config['SALT_SECRET']
            hashed_temp_password = hashlib.sha256((temp_password + salt).encode('utf-8')).hexdigest()
            usuario.temp_password = hashed_temp_password
            usuario.password = None

            # Guardar los cambios en la base de datos
            db.session.commit()

            # Preparar y enviar el correo electrónico
            parametro_nombre_empresa = Parametro.query.filter_by(clave='NOM-EMPRESA').first()
            nombre_empresa = parametro_nombre_empresa.valor if parametro_nombre_empresa else "Desconocido"
            
            datos_credenciales = {
                "nombreUsuario": f"{usuario.nombres} {usuario.apellidos}",
                "correoElectronico": usuario.email,
                "contrasenaTemporal": temp_password,
                "nombreEmpresa": nombre_empresa,  
            }
            asunto = "Credenciales de acceso actualizadas"
            contenido_html_credenciales = generar_plantilla('correo_restablecimiento_contraseña.html', datos_credenciales)
            
            # Función enviar_correo debe estar definida para manejar el envío de correos
            enviar_correo(usuario.email, asunto, contenido_html_credenciales)

            return response_success({"mensaje": "Contraseña restablecida exitosamente. Las nuevas credenciales han sido enviadas por correo electrónico."}, http_status=200)
        
        except SQLAlchemyError as e:
            db.session.rollback()
            return response_error(f"Error interno del servidor: {str(e)}", http_status=500)
        except Exception as e:
            db.session.rollback()
            return response_error(f"Error al enviar el correo: {str(e)}", http_status=500)

        
    
        
