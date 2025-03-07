from flask import Flask
import requests
import json
import urllib3
from datetime import datetime, timedelta
from hashlib import sha256
from utils.db import db
from models.facturas import Factura  
from models.proveedores_calificados import ProveedorCalificado
from config import Config  

# Configura tu conexión a la base de datos
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Suprime advertencias de solicitudes no seguras
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL del servicio web
URL = Config.WS_FACTURAJE_URL


# Función para generar hash de factura
def generar_hash(no_factura):
    return sha256(no_factura.encode('utf-8')).hexdigest()

# Función para codificar los caracteres especiales
def encode_response(data):
    """
    Codifica los caracteres especiales de una cadena JSON a UTF-8.
    """
    try:
        encoded_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
        print('Data codificada: \n', encoded_data, '\n')
        return encoded_data
    except Exception as e:
        print(f"Error al codificar: {e}")
        return None

# Función para decodificar los caracteres especiales
def decode_response(encoded_data):
    """
    Decodifica una cadena JSON UTF-8 a su formato original.
    """
    try:
        decoded_data = json.loads(encoded_data.decode('utf-8'))
        print('Data decodificada: \n', decoded_data, '\n')
        return decoded_data
    except Exception as e:
        print(f"Error al decodificar: {e}")
        return None

def almacenar_facturas():
    # Realiza la solicitud al web service
    response = requests.get(URL, verify=False)
    print(response.headers.get('Content-Type'))

    if response.status_code == 200:
        try:
            # Elimina BOM explícitamente antes de procesar
            content = response.content.lstrip(b'\xef\xbb\xbf')
            print("Contenido recibido antes de codificar/decodificar:", content[:500])

            # Decodifica el contenido JSON correctamente
            decoded_data = decode_response(content)
            if decoded_data is None:
                print("Error al decodificar la respuesta JSON.")
                return

            # Codifica y luego decodifica los datos para manejo seguro de caracteres
            re_encoded_data = encode_response(decoded_data)
            facturas = decode_response(re_encoded_data)

            # Limpia caracteres no válidos en todas las cadenas
            for factura in facturas:
                for key, value in factura.items():
                    if isinstance(value, str):
                        # Codifica y decodifica para eliminar caracteres inválidos
                        factura[key] = value.encode('utf-8', 'replace').decode('utf-8').strip()

        except json.JSONDecodeError as e:
            print(f"Error al decodificar el JSON: {e}")
            print("Contenido después de intentar limpiar el BOM:")
            print(content[:500])
            return

        # Calcula el rango de fechas
        fecha_actual = datetime.now()
        fecha_limite = fecha_actual - timedelta(days=15)

        # Filtra las facturas dentro del rango de fechas
        facturas_filtradas = [
            factura for factura in facturas
            if fecha_limite <= datetime.fromisoformat(factura['fecha_emision'].split(" ")[0]) <= fecha_actual
        ]

        # Preparar objetos para bulk insert
        nuevas_facturas = []

        with app.app_context():
            for factura in facturas_filtradas:
                # Verifica si el no_factura ya existe
                factura_existente = Factura.query.filter_by(no_factura=factura["no_factura"]).first()
                if factura_existente:
                    print(f"Factura con no_factura {factura['no_factura']} ya existe.")
                    continue  

                # Si no existe, crea un nuevo objeto Factura
                nueva_factura = Factura(
                    no_factura=factura["no_factura"],
                    monto=float(factura["Monto"]),
                    fecha_emision=datetime.fromisoformat(factura["fecha_emision"].split(" ")[0]),
                    fecha_vence=datetime.fromisoformat(factura["fecha_vence"].split(" ")[0]),
                    fecha_otorga=datetime.now(),
                    dias_credito=(datetime.fromisoformat(factura["fecha_vence"].split(" ")[0]) - datetime.fromisoformat(factura["fecha_emision"].split(" ")[0])).days,
                    nombre_proveedor=factura["razon_social"],
                    nit=factura["nit"],
                    factura_hash=generar_hash(factura["no_factura"]),
                    id_proveedor=1
                )
                nuevas_facturas.append(nueva_factura)

            # Bulk insert de todas las nuevas facturas
            if nuevas_facturas:
                db.session.bulk_save_objects(nuevas_facturas)
                db.session.commit()
                print(f"Se almacenaron {len(nuevas_facturas)} facturas nuevas.")
            else:
                print("No se encontraron facturas nuevas para almacenar.")
    else:
        print(f"Error al consultar el web service: {response.status_code}")



if __name__ == "__main__":
    almacenar_facturas()
