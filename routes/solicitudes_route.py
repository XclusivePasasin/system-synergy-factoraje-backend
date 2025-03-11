from datetime import datetime, time
from flask import Flask, request, Blueprint, send_file
from models.parametros import Parametro
from utils.db import db
from models.solicitudes import Solicitud
from models.facturas import Factura
from models.comentarios import Comentario
from models.proveedores_calificados import ProveedorCalificado
from sqlalchemy import and_, or_
from utils.response import response_success, response_error
from services.solicitudes_services import actualizar_solicitudes, exportar_solicitudes, generar_pdf_solicitud
from utils.interceptor import token_required
from services.email_service import *
from utils.bitacora import bitacora
from sqlalchemy.orm import joinedload

solicitud_bp = Blueprint('solicitud', __name__)

@solicitud_bp.route('/obtener-solicitudes', methods=['GET'])
@token_required
def obtener_solicitudes():
    try:
        # Obtener los parámetros de consulta
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        fecha_inicio = request.args.get('fecha_inicio')
        fecha_fin = request.args.get('fecha_fin')
        estado = request.args.get('estado')
        nombre_proveedor = request.args.get('nombre_proveedor')
        nrc = request.args.get('nrc')
        telefono = request.args.get('telefono')
        email = request.args.get('email')
        no_factura = request.args.get('no_factura')

        # Construir el query base
        query = db.session.query(Solicitud).join(Factura, Solicitud.id_factura == Factura.id).join(
            ProveedorCalificado, Factura.id_proveedor == ProveedorCalificado.id)

        # Filtros opcionales
        if fecha_inicio and fecha_fin:
            query = query.filter(Solicitud.fecha_solicitud.between(fecha_inicio, fecha_fin))
        if estado:
            query = query.filter(Solicitud.id_estado == estado)
        if nombre_proveedor:
            query = query.filter(ProveedorCalificado.razon_social.ilike(f"%{nombre_proveedor}%"))
        if nrc:
            query = query.filter(ProveedorCalificado.nrc.ilike(f"%{nrc}%"))
        if telefono:
            query = query.filter(ProveedorCalificado.telefono.ilike(f"%{telefono}%"))
        if email:
            query = query.filter(ProveedorCalificado.correo_electronico.ilike(f"%{email}%"))
        if no_factura:  
            query = query.filter(Factura.no_factura.ilike(f"%{no_factura}%"))

        # Paginación
        total_solicitudes = query.count()
        solicitudes = query.offset((page - 1) * per_page).limit(per_page).all()

        # Construir la respuesta
        response_data = {
            "current_page": page,
            "per_page": per_page,
            "total_pages": (total_solicitudes + per_page - 1) // per_page,
            "solicitudes": [
                {
                    "id": solicitud.id,
                    "nombre_cliente": solicitud.nombre_cliente,
                    "email": solicitud.email,
                    "iva": float(solicitud.iva),
                    "subtotal": float(solicitud.subtotal),
                    "total": float(solicitud.total),
                    "estado": solicitud.estado.clave ,
                    "id_estado": solicitud.id_estado,
                    "factura": {
                        "id": solicitud.factura.id,
                        "no_factura": solicitud.factura.no_factura,
                        "monto": float(solicitud.factura.monto),
                        "fecha_emision": solicitud.factura.fecha_emision.isoformat(),
                        "fecha_vence": solicitud.factura.fecha_vence.isoformat(),
                        "fecha_otorga": solicitud.factura.fecha_otorga.isoformat(),
                        "proveedor": {
                            key: getattr(solicitud.factura.proveedor, key)
                            for key in ProveedorCalificado.__table__.columns.keys()
                            if key not in ["cuenta_bancaria", "created_at", "updated_at"]
                        }
                    } if solicitud.factura else None
                } for solicitud in solicitudes
            ]
        }

        return response_success(response_data, "Consulta exitosa")
    except Exception as e:
        return response_error(f"Error al procesar la solicitud: {str(e)}", http_status=500)
    
@solicitud_bp.route('/obtener-detalle-solicitud', methods=['GET'])
@token_required
def obtener_detalle_solicitud():
    try:
        # Obtener el parámetro id de la solicitud desde la URL
        solicitud_id = request.args.get('id', type=int)
        
        if not solicitud_id:
            return response_error("El parámetro 'id' es obligatorio", http_status=400)

        # Buscar la solicitud por ID
        solicitud = db.session.query(Solicitud).filter_by(id=solicitud_id).first()

        if not solicitud:
            return response_error("La solicitud no existe", http_status=404)
        
        # Obtener el primer comentario asociado a la solicitud
        comentario = db.session.query(Comentario).filter_by(id_solicitud=solicitud_id).first()
        comentario_texto = comentario.comentario if comentario else None
        

        # Construir los datos de respuesta
        solicitud_data = {
            "solicitud": {
                "id": solicitud.id,
                "nombre_cliente": solicitud.nombre_cliente,
                "email": solicitud.email,
                "iva": float(solicitud.iva),
                "subtotal": float(solicitud.subtotal),
                "total": float(solicitud.total),
                "estado": solicitud.estado.clave if solicitud.estado else None,
                "id_estado": solicitud.id_estado,
                "fecha_solicitud": solicitud.fecha_solicitud.strftime("%d/%m/%Y"),
                "fecha_aprobacion": solicitud.fecha_aprobacion.strftime("%d/%m/%Y") if solicitud.fecha_aprobacion else None,
                
                "factura": {
                    "id": solicitud.factura.id,
                    "no_factura": solicitud.factura.no_factura,
                    "fecha_otorga": solicitud.factura.fecha_otorga.strftime("%d/%m/%Y"),
                    "fecha_vence": solicitud.factura.fecha_vence.strftime("%d/%m/%Y"),
                    "monto": float(solicitud.factura.monto),
                    "pronto_pago": float(solicitud.subtotal) - float(solicitud.iva),
                    "proveedor": {
                        "id": solicitud.factura.proveedor.id,
                        "razon_social": solicitud.factura.proveedor.razon_social,
                        "correo_electronico": solicitud.factura.proveedor.correo_electronico,
                        "telefono": solicitud.factura.proveedor.telefono,
                    }
                } if solicitud.factura else None,
                "comentario": comentario_texto  
            }
        }

        return response_success(solicitud_data, "Consulta exitosa")
    except Exception as e:
        return response_error(f"Error al procesar la solicitud: {str(e)}", http_status=500)
    
@solicitud_bp.route('/aprobar', methods=['PUT'])
@token_required
@bitacora(modulo="Solicitudes", accion="Aprobación de solicitud")  
def aprobar_solicitud():
    try:
        solicitud_id = request.args.get('id', type=int)
        if not solicitud_id:
            return response_error("El parámetro 'id' es obligatorio", http_status=400)

        data = request.get_json()
        id_aprobador = data.get('id_aprobador')  
        comentario = data.get('comentario', None)

        if not id_aprobador:
            return response_error("El campo 'id_aprobador' es obligatorio", http_status=400)

        # Buscar la solicitud por ID
        solicitud = db.session.query(Solicitud).filter_by(id=solicitud_id).first()
        if not solicitud:
            return response_error("La solicitud no existe", http_status=404)

         # Validar si la solicitud ya está aprobada o denegada
        if solicitud.id_estado in [2, 3]:
            estado = "aprobada" if solicitud.id_estado == 2 else "denegada"
            return response_error(f"La solicitud ya fue {estado}. No se puede cambiar su estado.", http_status=409)

        # Obtener el id_factura asociado a la solicitud
        id_factura = solicitud.id_factura
        
        # Actualizar el estado de la solicitud
        solicitud.id_estado = 2  
        solicitud.fecha_aprobacion = db.func.now()
        solicitud.id_aprobador = id_aprobador  

        # Registrar comentario si se proporciona
        if comentario:
            nuevo_comentario = Comentario(
                id_solicitud=solicitud_id,
                id_factura=id_factura,
                comentario=comentario,
                created_at=db.func.now(),
                updated_at=db.func.now()
            )
            db.session.add(nuevo_comentario)

        # Guardar cambios en la base de datos
        db.session.commit()
        
        # Obtener los parámetros adicionales de la base de datos
        parametros = Parametro.query.filter(Parametro.clave.in_(['NOM-EMPRESA', 'ENC-EMPRESA', 'TEL-EMPRESA'])).all()
        parametros_dict = {param.clave: param.valor for param in parametros}

        nombre_empresa = parametros_dict.get('NOM-EMPRESA', 'Nombre Empresa No Definido')
        nombre_encargado = parametros_dict.get('ENC-EMPRESA', 'Encargado No Definido')
        telefono_empresa = parametros_dict.get('TEL-EMPRESA', 'Teléfono No Definido')

        # Enviar correo al usuario notificando la aprobación
        datos_aprobacion = {
            "nombreSolicitante": solicitud.nombre_cliente,
            "noFactura": solicitud.factura.no_factura,
            "montoFactura": f"${solicitud.total:.2f}",
            "descuento": f"${solicitud.descuento_app:.2f}",
            "iva": f"${solicitud.iva:.2f}",
            "subtotal": f"${solicitud.subtotal:.2f}",
            "fechaSolicitud": solicitud.fecha_solicitud.strftime("%d/%m/%Y"),
            "fechaVencimiento": solicitud.factura.fecha_vence.strftime("%d/%m/%Y"),
            "diasCredito": (solicitud.factura.fecha_vence - solicitud.fecha_aprobacion).days,
            "nombreEmpresa": nombre_empresa,
            "nombreEncargadoEmpresa": nombre_encargado,
            "telefonoEmpresa": telefono_empresa
        }
        asunto = f"Solicitud de Pronto Pago Aprobada FACTURA {datos_aprobacion['noFactura']}"
        contenido_html_aprobacion = generar_plantilla('correo_aprobacion_solicitud_pp.html', datos_aprobacion)

        # Enviar correo al cliente
        enviar_correo(solicitud.email, asunto, contenido_html_aprobacion)

        # Construir respuesta
        solicitud_data = {
            "id": solicitud.id,
            "nombre_cliente": solicitud.nombre_cliente,
            "contacto": solicitud.contacto,
            "email": solicitud.email,
            "id_estado": solicitud.id_estado,
            "id_aprobador": solicitud.id_aprobador,  
            "fecha_aprobacion": solicitud.fecha_aprobacion.isoformat() if solicitud.fecha_aprobacion else None,
            "total": float(solicitud.total),
            "factura": {
                "id": solicitud.factura.id,
                "no_factura": solicitud.factura.no_factura,
                "monto": float(solicitud.factura.monto),
                "proveedor": {
                    "id": solicitud.factura.proveedor.id,
                    "razon_social": solicitud.factura.proveedor.razon_social
                }
            } if solicitud.factura else None
        }

        return response_success({"solicitud": solicitud_data}, "Solicitud aprobada exitosamente. Correo de notificación enviado.")
    except Exception as e:
        return response_error(f"Error al procesar la solicitud: {str(e)}", http_status=500)




@solicitud_bp.route('/desaprobar', methods=['PUT'])
@token_required
@bitacora(modulo="Solicitudes", accion="Desaprobación de solicitud")  # Decorador que registra la bitácora
def desaprobar_solicitud():
    try:
        # Obtener el ID de la solicitud desde los query parameters
        solicitud_id = request.args.get('id', type=int)
        if not solicitud_id:
            return response_error("El parámetro 'id' es obligatorio", http_status=400)

        # Obtener datos del body
        data = request.get_json()
        id_aprobador = data.get('id_aprobador')
        comentario = data.get('comentario', None)

        # Validar que el campo id_aprobador sea obligatorio
        if not id_aprobador:
            return response_error("El parámetro 'id_aprobador' es obligatorio", http_status=400)

        # Buscar la solicitud por ID
        solicitud = db.session.query(Solicitud).filter_by(id=solicitud_id).first()
        if not solicitud:
            return response_error("La solicitud no existe", http_status=404)

        # Validar si la solicitud ya está denegada
        if solicitud.id_estado in [2, 3]:
            estado = "aprobada" if solicitud.id_estado == 2 else "denegada"
            return response_error(f"La solicitud ya fue {estado}. No se puede cambiar su estado.", http_status=409)

        # Obtener el id_factura asociado a la solicitud
        id_factura = solicitud.id_factura

        # Actualizar el estado de la solicitud
        solicitud.id_estado = 3  
        solicitud.fecha_aprobacion = None  
        solicitud.id_aprobador = id_aprobador  

        # Registrar comentario si se proporciona
        if comentario:
            nuevo_comentario = Comentario(
                id_solicitud=solicitud_id,
                id_factura=id_factura, 
                comentario=comentario,
                created_at=db.func.now(),
                updated_at=db.func.now()
            )
            db.session.add(nuevo_comentario)

        # Guardar cambios en la base de datos
        db.session.commit()
        
        # Obtener los parámetros adicionales de la base de datos
        parametros = Parametro.query.filter(Parametro.clave.in_(['NOM-EMPRESA', 'ENC-EMPRESA', 'TEL-EMPRESA'])).all()
        parametros_dict = {param.clave: param.valor for param in parametros}

        nombre_empresa = parametros_dict.get('NOM-EMPRESA', 'Nombre Empresa No Definido')
        nombre_encargado = parametros_dict.get('ENC-EMPRESA', 'Encargado No Definido')
        telefono_empresa = parametros_dict.get('TEL-EMPRESA', 'Teléfono No Definido')

        # Enviar correo al usuario notificando la denegación
        datos_denegacion = {
            "nombreSolicitante": solicitud.nombre_cliente,
            "noFactura": solicitud.factura.no_factura,
            "montoFactura": f"${solicitud.total:.2f}",
            "fechaSolicitud": solicitud.fecha_solicitud.strftime("%d/%m/%Y"),
            "nombreEmpresa": nombre_empresa,
            "nombreEncargadoEmpresa": nombre_encargado,
            "telefonoEmpresa": telefono_empresa
        }
        asunto = f"Solicitud de Pronto Pago Denegada FACTURA {datos_denegacion['noFactura']}"
        contenido_html_denegacion = generar_plantilla('correo_denegacion_solicitud_pp.html', datos_denegacion)

        # Enviar correo al cliente
        enviar_correo(solicitud.email, asunto, contenido_html_denegacion)

        # Construir respuesta
        solicitud_data = {
            "id": solicitud.id,
            "nombre_cliente": solicitud.nombre_cliente,
            "contacto": solicitud.contacto,
            "email": solicitud.email,
            "id_estado": solicitud.id_estado,
            "total": float(solicitud.total),
            "factura": {
                "id": solicitud.factura.id,
                "no_factura": solicitud.factura.no_factura,
                "monto": float(solicitud.factura.monto),
                "proveedor": {
                    "id": solicitud.factura.proveedor.id,
                    "razon_social": solicitud.factura.proveedor.razon_social
                }
            } if solicitud.factura else None
        }

        return response_success({"solicitud": solicitud_data}, "Solicitud denegada exitosamente. Correo de notificación enviado.")
    except Exception as e:
        return response_error(f"Error al procesar la solicitud: {str(e)}", http_status=500)


@solicitud_bp.route('/panel-solicitudes', methods=['GET'])
@token_required
def panel_solicitudes():
    try:
        # Obtener parámetros de filtro de fechas
        fecha_inicio = request.args.get('fecha_inicio')  # Ejemplo: '2024-12-01'
        fecha_fin = request.args.get('fecha_fin')  # Ejemplo: '2024-12-05'

        # Validar fechas
        if fecha_inicio and fecha_fin:
            try:
                # Convertir las fechas a objetos datetime
                fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
                fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
                # Ajustar rango al día completo
                fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
                fecha_fin = datetime.combine(fecha_fin, datetime.max.time())
            except ValueError:
                return response_error("Las fechas deben estar en formato 'YYYY-MM-DD'", http_status=400)

        # Construir consultas con filtros opcionales
        base_query = db.session.query(Solicitud)

        if fecha_inicio and fecha_fin:
            base_query = base_query.filter(Solicitud.fecha_solicitud.between(fecha_inicio, fecha_fin))

        # Consultas específicas para métricas del panel
        total_solicitudes_query = base_query.filter(Solicitud.id_estado.in_([1, 2, 3]))
        solicitudes_aprobadas_query = base_query.filter(Solicitud.id_estado == 2)
        solicitudes_sin_aprobar_query = base_query.filter(Solicitud.id_estado == 1)
        solicitudes_denegadas_query = base_query.filter(Solicitud.id_estado == 3)

        # Contar resultados
        total_solicitudes = total_solicitudes_query.count()
        solicitudes_aprobadas = solicitudes_aprobadas_query.count()
        solicitudes_sin_aprobar = solicitudes_sin_aprobar_query.count()
        solicitudes_denegadas = solicitudes_denegadas_query.count()

        # Construir respuesta
        response_data = {
            "total_solicitudes": total_solicitudes,
            "solicitudes_aprobadas": solicitudes_aprobadas,
            "solicitudes_sin_aprobar": solicitudes_sin_aprobar,
            "solicitudes_denegadas": solicitudes_denegadas,
            "filtros_aplicados": {
                "fecha_inicio": fecha_inicio.strftime("%Y-%m-%d") if fecha_inicio else None,
                "fecha_fin": fecha_fin.strftime("%Y-%m-%d") if fecha_fin else None
            }
        }

        return response_success(response_data, "Métricas de solicitudes obtenidas con éxito")
    except Exception as e:
        return response_error(f"Error al procesar la solicitud: {str(e)}", http_status=500)


@solicitud_bp.route('/procesar-solicitudes', methods=['POST'])
@token_required
def procesar_solicitudes_route():
    """
    Recibe una lista de valores unicos y llama al servicio para procesar las solicitudes y exportar la información en un archivo de Excel.
    """
    try:
        data = request.get_json()
        lista_ids = data.get("ids", [])

        # Actualizar las solicitudes estado a 'Procesada'
        cantidad_actualizadas, error = actualizar_solicitudes(lista_ids)
        if error:
            return response_error(error, http_status=400)

        # Exportar las solicitudes en un formato Excel
        archivo = exportar_solicitudes(lista_ids)
        
        # Si exportar_solicitudes devuelve un error, manejarlo
        if isinstance(archivo, tuple) and archivo[1] == 400:  # Si es un error
            return archivo  # Devuelve el error directamente
        
        # Devolver el archivo generado
        return archivo

    except Exception as e:
        return response_error(f"Error en la ruta: {str(e)}", http_status=500)


@solicitud_bp.route('/generar-pdf', methods=['GET'])
@token_required
def generar_pdf_route():
    """
    Genera un PDF con los detalles de una solicitud específica.
    El ID de la solicitud se recibe como query parameter: ?id_solicitud=1
    """
    try:
        # Obtener el id_solicitud del query parameter
        id_solicitud = request.args.get('id_solicitud', type=int)
        if id_solicitud is None:
            return response_error("El parámetro id_solicitud es requerido", http_status=400)

        # Obtener la solicitud de la base de datos con sus relaciones
        solicitud = Solicitud.query.options(
            joinedload(Solicitud.factura).joinedload(Factura.proveedor)
        ).get(id_solicitud)
        
        if not solicitud:
            return response_error("Solicitud no encontrada", http_status=404)

        # Generar el PDF usando el servicio
        pdf_buffer = generar_pdf_solicitud(solicitud)
        
        # Generar nombre del archivo
        nombre_archivo = f"Solicitud_{solicitud.factura.no_factura}_{datetime.now().strftime('%d-%m-%Y')}.pdf"
        
        # Enviar el archivo PDF como respuesta
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=nombre_archivo
        )

    except Exception as e:
        return response_error(f"Error al generar el PDF: {str(e)}", http_status=500)