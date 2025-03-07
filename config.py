import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", None)
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() in ["true", "1", "t"]
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "clobitechnologiesdevelopmentse@gmail.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "vhok gjmx gfge inab")
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "True").lower() in ["true", "1", "t"]
    SALT_SECRET = os.getenv('SALT_SECRET') 
    WS_FACTURAJE_URL = os.getenv("WS_FACTURAJE_URL")
    URL_API = os.getenv("URL_API_SERVER")