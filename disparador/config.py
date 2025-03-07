import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import urllib3

# Cargar variables de entorno
load_dotenv()

# Configuración de la aplicación
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", None)
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() in ["true", "1", "t"]
app.config["WS_FACTURAJE_URL"] = os.getenv("WS_FACTURAJE_URL")
app.config["URL_API_BACKEND"] = os.getenv("URL_API_BACKEND")
app.config["USER_LOGIN"] = os.getenv("USER_LOGIN")
app.config["PASSWORD_LOGIN"] = os.getenv("PASSWORD_LOGIN")

# Inicializar base de datos
db = SQLAlchemy(app)

# Suprimir advertencias de solicitudes no seguras
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
