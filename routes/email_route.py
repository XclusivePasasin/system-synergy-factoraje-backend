from flask import Blueprint, jsonify, request
from services.email_service import generar_plantilla, enviar_correo
from utils.interceptor import token_required
from utils.response import response_success, response_error
from models.parametros import Parametro
from config import Config

email_bp = Blueprint('email', __name__)

@email_bp.route('/enviar-email', methods=['POST'])
@token_required
def enviar_email():
    try:
        # Obtenemos JSON de la petición
        datos = request.json

        # Validamos que los campos requeridos estén presentes
        campos_principales = ['destinatario', 'asunto', 'datos']
        for campo in campos_principales:
            if campo not in datos:
                return response_error(f"El campo {campo} es obligatorio", http_status=400)
            
        # Obtener los parámetros adicionales de la base de datos
        parametros = Parametro.query.filter(Parametro.clave.in_(['NOM-EMPRESA', 'ENC-EMPRESA', 'TEL-EMPRESA'])).all()
        parametros_dict = {param.clave: param.valor for param in parametros}

        nombre_empresa = parametros_dict.get('NOM-EMPRESA', 'Nombre Empresa No Definido')
        nombre_encargado = parametros_dict.get('ENC-EMPRESA', 'Encargado No Definido')
        telefono_empresa = parametros_dict.get('TEL-EMPRESA', 'Teléfono No Definido')

        # Validamos que los campos requeridos dentro de 'datos' estén presentes
        datos_plantilla = datos['datos']
        campos_datos = [
            'nombreEmpresa', 'noFactura', 'monto', 
            'fechaOtorgamiento', 'fechaVencimiento', 
            'diasCredito','factura_hash'
        ]  
        
        for campo in campos_datos:
            if campo not in datos_plantilla:
                return response_error(f"El campo {campo} es obligatorio dentro de 'datos'", http_status=400)

        # Agregar variables adicionales a datos_plantilla
        datos_plantilla.update({
            'nombreEmpresaEncargada': nombre_empresa,
            'nombreEncargadoEmpresa': nombre_encargado,
            'telefonoEmpresa': telefono_empresa
        })

        # Generar dinámicamente el link del botón
        no_factura = datos_plantilla['factura_hash'] # Enviamos el hash de la factura para realizar la busqueda de forma segura
        datos_plantilla['linkBoton'] = f"{Config.URL_API}/solicitar-pronto-pago?no_factura={no_factura}"

        # Generamos el contenido HTML usando la plantilla
        contenido_html = generar_plantilla('correo_template.html', datos_plantilla)

        if not contenido_html:
            return response_error("Error al generar el contenido del correo", http_status=500)

        # Enviamos el correo
        resultado = enviar_correo(
            destinatario=datos['destinatario'], 
            asunto=datos['asunto'], 
            contenido_html=contenido_html
        )

        if resultado:
            return response_success(data=None, message="Correo enviado exitosamente", http_status=200)
        else:
            return response_error("No se pudo enviar el correo", http_status=500)

    except Exception as e:
        return response_error("Ocurrió un error interno", http_status=500)
