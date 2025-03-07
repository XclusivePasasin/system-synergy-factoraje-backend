from flask import Blueprint, request
from utils.metricas import metrica_factura
import logging
from datetime import datetime, timedelta
from models.parametros import Parametro
from models.solicitudes import Solicitud
from models.facturas import Factura
from models.usuarios import Usuario
from models.roles import Rol
from utils.db import db
from utils.response import response_success, response_error
from utils.interceptor import token_required
from services.email_service import *
from sqlalchemy import *

facturas_bp = Blueprint('factura', __name__)

@facturas_bp.route('/obtener-detalle-factura', methods=['GET'])
@token_required
def obtener_detalle_factura():
    try:
        # Obtener el parámetro no_factura desde la URL
        no_factura = request.args.get('no_factura')
        if not no_factura:
            return response_error("El parámetro no_factura es obligatorio", http_status=409)

        # Consulta para obtener los detalles de la factura
        factura = Factura.query.filter(
            or_(Factura.factura_hash == no_factura, Factura.no_factura == no_factura)
        ).first()
        if not factura:
            return response_error(f"No se encontró una factura con el número: {no_factura}", http_status=404)

        # Calcular los días restantes para el vencimiento
        
        # Crear una fecha manual: año, mes, día, hora, minuto, segundo
        # fecha_actual = datetime(2024, 12, 24, 00, 00, 00)
        fecha_actual = datetime.now()
        dias_restantes = (factura.fecha_vence - fecha_actual).days

        # Determinar el estado de la solicitud en función de los días restantes
        if dias_restantes < 0:
            estado_solicitud = 4  
        else:
            # Consultar el estado de la solicitud de pronto pago
            solicitud = Solicitud.query.filter_by(id_factura=factura.id).first()
            estado_solicitud = solicitud.id_estado if solicitud else 0

        # Obtener el parámetro de interés anual
        parametro = Parametro.query.filter_by(clave='INT_AN_PP').first()
        if not parametro:
            return response_error("No se encontró ningún parámetro en la tabla", http_status=500)

        try:
            interes_anual = float(parametro.valor)
        except ValueError:
            return response_error("El valor del parámetro de interés anual no es válido", http_status=500)

        # Calcular la métrica con los datos obtenidos
        resultado = metrica_factura(dias_restantes, float(factura.monto), interes_anual)

        # Preparar los detalles de la factura dentro del nodo "facturas"
        resultado_final = {
            "factura": {
                "nombre_proveedor": factura.nombre_proveedor,
                "no_factura": factura.no_factura,
                "factura_hash": factura.factura_hash,
                "dias_restantes": dias_restantes,
                "fecha_otorga": datetime.now().strftime("%d/%m/%Y"),
                "fecha_vence": factura.fecha_vence.strftime("%d/%m/%Y"),
                "monto": float(factura.monto),
                "estado": estado_solicitud,
                **resultado
            }
        }

        return response_success(resultado_final, "Detalle de factura obtenido correctamente", http_status=200)
    except Exception as e:
        return response_error(str(e), http_status=500)



@facturas_bp.route('/solicitar-pago-factura', methods=['POST'])
@token_required
def solicitar_pago_factura():
    try:
        datos = request.json

        if 'data' not in datos or 'factura' not in datos['data']:
            return response_error("El nodo 'data.factura' es obligatorio", http_status=409)

        data = datos['data']

        campos_adicionales = ['nombre_solicitante', 'cargo', 'email']
        for campo in campos_adicionales:
            if campo not in data:
                return response_error(f"El campo {campo} en 'data' es obligatorio", http_status=409)

        facturas_data = data['factura']
        campos_factura = [
            'nombre_proveedor', 'no_factura', 'fecha_otorga', 'fecha_vence',
            'monto', 'iva', 'descuento_app', 'subtotal', 'total'
        ]
        for campo in campos_factura:
            if campo not in facturas_data:
                return response_error(f"El campo {campo} en 'factura' es obligatorio", http_status=409)

        # Validar que la factura exista por no_factura
        factura_existente = Factura.query.filter(
            or_(
                Factura.factura_hash == facturas_data['no_factura'],
                Factura.no_factura == facturas_data['no_factura']
            )
        ).first()
        if not factura_existente:
            return response_error("La solicitud proporcionada no existe en la base de datos", http_status=409)

        # Validar que la solicitud no exista ya para esa factura
        solicitud_existente = Solicitud.query.filter_by(id_factura=factura_existente.id).first()
        if solicitud_existente:
            return response_error("La solicitud ya fue procesada", http_status=409)

        # Validar formato de fecha
        try:
            fecha_vencimiento = datetime.strptime(facturas_data['fecha_vence'], "%d/%m/%Y")
        except ValueError:
            return response_error("Formato de fecha inválido. Use DD/MM/YYYY", http_status=409)

        fecha_actual = datetime.now()
        if fecha_actual > fecha_vencimiento:
            return response_error("El tiempo de otorgamiento ha expirado", http_status=409)

        dias = (fecha_vencimiento - fecha_actual).days
        if dias < 0:
            return response_error("La fecha de vencimiento ha expirado", http_status=409)


        # Calcular fecha de otorgamiento (un día después, ajustando para fines de semana)
        fecha_otorga = fecha_actual + timedelta(days=1 if fecha_actual.weekday() != 4 else 3)
        # Actualizar el campo fecha_otorga de la factura existente
        factura_existente.fecha_otorga = fecha_otorga
        db.session.commit()
        
        # Asignar la fecha de otorgamiento a la fecha actual
        # factura_existente.fecha_otorga = fecha_actual
        # db.session.commit()
        
        # Crear la nueva solicitud
        nueva_solicitud = Solicitud(
            nombre_cliente=data['nombre_solicitante'],  
            contacto=factura_existente.proveedor.telefono,  
            email=data['email'],
            cargo=data['cargo'],
            descuento_app=facturas_data['descuento_app'],
            iva=facturas_data['iva'],
            subtotal=facturas_data['subtotal'],
            total=facturas_data['total'],
            fecha_solicitud=fecha_actual,
            id_factura=factura_existente.id,
            id_estado=1  
        )

        db.session.add(nueva_solicitud)
        db.session.commit()

        # Obtener los parámetros adicionales de la base de datos
        parametros = Parametro.query.filter(Parametro.clave.in_(['NOM-EMPRESA', 'ENC-EMPRESA', 'TEL-EMPRESA','MAIL-EMPRESA'])).all()
        parametros_dict = {param.clave: param.valor for param in parametros}

        nombre_empresa = parametros_dict.get('NOM-EMPRESA', 'Nombre Empresa No Definido')
        nombre_encargado = parametros_dict.get('ENC-EMPRESA', 'Encargado No Definido')
        telefono_empresa = parametros_dict.get('TEL-EMPRESA', 'Teléfono No Definido')
        email_empresa = parametros_dict.get('MAIL-EMPRESA', 'Email No Definido')

        # Datos para el correo de confirmación al proveedor
        datos_confirmacion = {
            "nombreSolicitante": data['nombre_solicitante'],
            "noFactura": factura_existente.id,
            "monto": f"${facturas_data['monto']}",
            "fechaSolicitud": fecha_actual.strftime("%d/%m/%Y"),
            "nombreEmpresa": nombre_empresa,
            "nombreEncargadoEmpresa": nombre_encargado,
            "telefonoEmpresa": telefono_empresa,
        }
        asunto_confirmacion = f"Confirmación de Recepción de su Solicitud de Pronto Pago FACTURA {datos_confirmacion['noFactura']}"
        contenido_html_confirmacion = generar_plantilla('correo_confirmacion_solicitud_pp.html', datos_confirmacion)

        # Enviar correo de confirmación al proveedor
        enviar_correo(data['email'], asunto_confirmacion, contenido_html_confirmacion)

       # Obtener los usuarios con rol "Operador de ICC"
        usuarios_contadores = Usuario.query.join(Rol).filter(Rol.rol == "Operador de ICC").all()

        # Verificar si hay usuarios con el rol
        if not usuarios_contadores:
            return response_error("No se encontraron usuarios con el rol de Contador para enviar la notificación.", http_status=404)

        # Enviar notificación a cada contador
        for contador in usuarios_contadores:
            datos_notificacion = {
                "nombreContador": f"{contador.nombres} {contador.apellidos}",
                "proveedor": facturas_data['nombre_proveedor'],
                "noFactura": factura_existente.id,
                "montoFactura": f"${float(facturas_data['monto']):.2f}",
                "fechaSolicitud": fecha_actual.strftime("%d/%m/%Y"),
                "diasCredito": dias,
                "nombreEmpresa": nombre_empresa
            }
            asunto_notificacion = f"Nueva Solicitud de Pronto Pago en Espera de Gestión FACTURA {datos_notificacion['noFactura']}"
            contenido_html_notificacion = generar_plantilla('correo_notificacion_solicitud_pendiente_aprobacion_pp.html', datos_notificacion)
            
            # Enviar correo a cada contador
            enviar_correo(contador.email, asunto_notificacion, contenido_html_notificacion)
            print(f"Enviado correo notificacion a {contador.email}")
            # Actualizar el campo noti_contador de la factura
            factura_existente.noti_contador = 'S'
            db.session.commit()
            logging.info(f"Factura con no_factura {factura_existente.no_factura} marcada como notificada a los contadores.")

        return response_success("Solicitud creada exitosamente. Los correos de confirmación y notificación han sido enviados.", http_status=201)
    except Exception as e:
        return response_error(str(e), http_status=500)




