import logging
import os
from config import app, db
from models import Factura, ProveedorCalificado
import requests
from datetime import datetime, timedelta
from hashlib import sha256
import json
import traceback


# Obtener el directorio actual donde está 'main.py'
base_dir = os.path.dirname(__file__)

# Definir el path para el archivo de log dentro de 'disparador'
log_file = os.path.join(base_dir, 'app.log')

# Configuración del logger
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Variables globales
token = None
token_expiration = None

# Función para generar hash de factura
def generar_hash(no_factura):
    return sha256(no_factura.encode('utf-8')).hexdigest()

# Función para codificar los caracteres especiales
def encode_response(data):
    try:
        encoded_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        return encoded_data
    except Exception as e:
        logging.error(f"Error al codificar: {e}")
        return None

# Función para decodificar los caracteres especiales
def decode_response(encoded_data):
    try:
        decoded_data = json.loads(encoded_data.decode('utf-8'))
        return decoded_data
    except Exception as e:
        logging.error(f"Error al decodificar: {e}")
        return None

# Función para iniciar sesión y obtener el token
def obtener_token():
    global token, token_expiration

    login_url = f"{app.config['URL_API_BACKEND']}/api/usuario/inicio-sesion"
    credentials = {
        "email": app.config["USER_LOGIN"],
        "password": app.config["PASSWORD_LOGIN"]
    }

    try:
        response = requests.post(login_url, json=credentials, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data["data"]["access_token"]
            expires_in = data["data"]["expires_in"]
            token_expiration = datetime.now() + timedelta(seconds=expires_in)
            logging.info("Token obtenido exitosamente.")
        else:
            logging.error(f"Error al obtener el token: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error al obtener el token: {e}")

def validar_monto_factoraje(id_proveedor, monto_factura):
    """
    Valida si el monto de la factura está dentro del rango permitido por el proveedor.
    
    :param id_proveedor: ID del proveedor en la base de datos.
    :param monto_factura: Monto de la factura a validar.
    :return: True si el monto está permitido, False en caso contrario.
    """
    with app.app_context():
        # Buscar el proveedor en la base de datos
        proveedor = ProveedorCalificado.query.filter_by(id=id_proveedor).first()

        if not proveedor:
            logging.warning(f"No se encontró un proveedor con ID {id_proveedor}.")
            return False

        # Validar si el monto está dentro del rango permitido
        if proveedor.monto_minimo_factoraje <= monto_factura <= proveedor.monto_maximo_factoraje:
            return True
        else:
            logging.warning(
                f"El monto {monto_factura} no cumple con los requisitos de factoraje del proveedor {proveedor.razon_social}. "
                f"Rango Permitido: [{proveedor.monto_minimo_factoraje} - {proveedor.monto_maximo_factoraje}]"
            )
            return False


# Función para almacenar facturas
def almacenar_facturas():
    # Nueva URL del endpoint local
    URL = f"{app.config['URL_API_BACKEND']}/api/wsFactoraje/"
    logging.info(f"Iniciando proceso de almacenamiento de facturas. URL del endpoint: {URL}")

    try:
        response = requests.get(URL, verify=False)
        logging.info(f"Solicitud al endpoint realizada. Código de estado: {response.status_code}")

        if response.status_code == 200:
            try:
                # Decodificar respuesta JSON
                facturas = response.json()
                logging.info(f"Respuesta JSON recibida. Total de facturas obtenidas: {len(facturas)}")

                fecha_actual = datetime.now()
                fecha_limite = fecha_actual - timedelta(days=90)
                logging.info(f"Fecha actual: {fecha_actual}. Fecha límite: {fecha_limite}")

                # Filtrar facturas dentro del rango de fechas y que no estén vencidas
                facturas_filtradas = [
                    factura for factura in facturas
                    if fecha_limite <= datetime.fromisoformat(factura['fecha_emision'].split(" ")[0]) <= fecha_actual
                    and datetime.fromisoformat(factura['fecha_vence'].split(" ")[0]) >= fecha_actual
                ]
                logging.info(f"Facturas filtradas dentro del rango: {len(facturas_filtradas)}")

                nuevas_facturas = []
                with app.app_context():
                    for factura in facturas_filtradas:
                        logging.info(f"Procesando factura: {factura['no_factura']}")

                        # Verificar si la factura ya existe
                        factura_existente = Factura.query.filter_by(no_factura=factura["no_factura"]).first()
                        if factura_existente:
                            logging.info(f"Factura con no_factura {factura['no_factura']} ya existe. Se omite.")
                            continue

                        # Obtener ID del proveedor desde la factura
                        id_proveedor = factura["id"]
                        monto_factura = float(factura["Monto"])

                        # Validar el factoraje antes de continuar
                        if not validar_monto_factoraje(id_proveedor, monto_factura):
                            logging.info(f"Factura {factura['no_factura']} no cumple con los requisitos de factoraje y será omitida.")
                            continue  # Omitir la factura si no cumple con el rango permitido

                        # Calcular fecha de otorgamiento (un día después, ajustando para fines de semana)
                        fecha_otorga = fecha_actual + timedelta(days=1 if fecha_actual.weekday() != 4 else 3)
                        logging.info(f"Fecha de otorgamiento calculada: {fecha_otorga}")

                        # Crear el objeto Factura
                        nueva_factura = Factura(
                            no_factura=factura["no_factura"],
                            monto=monto_factura,
                            fecha_emision=datetime.fromisoformat(factura["fecha_emision"].split(" ")[0]),
                            fecha_vence=datetime.fromisoformat(factura["fecha_vence"].split(" ")[0]),
                            fecha_otorga=fecha_otorga,
                            dias_credito=(datetime.fromisoformat(factura["fecha_vence"].split(" ")[0]) - datetime.fromisoformat(factura["fecha_emision"].split(" ")[0])).days,
                            nombre_proveedor=factura["razon_social"],
                            nit=factura["nit"],
                            factura_hash=generar_hash(factura["no_factura"]),
                            id_proveedor=id_proveedor  # Asignar correctamente el ID del proveedor
                        )
                        nuevas_facturas.append(nueva_factura)

                    # Almacenar nuevas facturas si hay alguna
                    if nuevas_facturas:
                        db.session.bulk_save_objects(nuevas_facturas)
                        db.session.commit()
                        logging.info(f"Se almacenaron {len(nuevas_facturas)} facturas nuevas.")
                    else:
                        logging.info("No se encontraron facturas nuevas para almacenar.")
            except Exception as e:
                logging.error(f"Error procesando datos: {e}")
                logging.error(traceback.format_exc())
        else:
            logging.error(f"Error al consultar el endpoint local: {response.status_code}")
    except Exception as e:
        logging.error(f"Error al realizar la solicitud: {e}")
        logging.error(traceback.format_exc())

# Función para enviar correos electrónicos
def enviar_correos_facturas_no_notificadas():
    global token, token_expiration
    if not token or datetime.now() >= token_expiration:
        obtener_token()

    if not token:
        logging.error("No se pudo obtener el token. No se enviarán correos.")
        return

    with app.app_context():
        facturas_no_notificadas = Factura.query.filter_by(noti_cliente='N').all()

        for factura in facturas_no_notificadas:
            # Se realiza una busqueda del correo electronico a traves de la tabla de proveedores calificados para obtenerlo y enviarle la informacion de la factura.
            proveedor = ProveedorCalificado.query.filter_by(id=factura.id_proveedor).first()
            if not proveedor or not proveedor.correo_electronico:
                logging.warning(f"No se encontró correo para el proveedor de la factura {factura.no_factura}")
                continue

            payload = {
                "destinatario": proveedor.correo_electronico,   
                "asunto": "Opción de Pronto Pago Disponible",
                "datos": {
                    "nombreEmpresa": proveedor.razon_social,
                    "noFactura": factura.no_factura,
                    "factura_hash": factura.factura_hash,
                    "monto": str(factura.monto),
                    "fechaOtorgamiento": factura.fecha_otorga.strftime("%d/%m/%Y"),
                    "fechaVencimiento": factura.fecha_vence.strftime("%d/%m/%Y"),
                    "diasCredito": str(factura.dias_credito)
                }
            }
            try:
                response = requests.post(
                    f"{app.config['URL_API_BACKEND']}/api/email/enviar-email",
                    json=payload,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=10
                )
                if response.status_code == 200:
                    factura.noti_cliente = 'S'
                    db.session.commit()
                    logging.info(f"Correo enviado para la factura {factura.no_factura}.")
            except Exception as e:
                logging.error(f"Error al enviar correo para la factura {factura.no_factura}: {e}")

if __name__ == "__main__":
    with app.app_context():
        almacenar_facturas()
        enviar_correos_facturas_no_notificadas()
