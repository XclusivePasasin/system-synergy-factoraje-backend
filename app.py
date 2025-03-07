from flask import Flask
from extensions import db, migrate
# Modelos
from models.usuarios import Usuario
from models.facturas import Factura
from models.roles import Rol
from models.estados import Estado
from models.solicitudes import Solicitud
from models.proveedores_calificados import ProveedorCalificado
from models.comentarios import Comentario
from models.bitacoras import Bitacora
from models.permisos import Permiso
from models.menus import Menu
from models.parametros import Parametro
from models.desembolsos import Desembolso
#Seeds
from seeds.seeds import init_app
# Rutas
from routes.email_route import email_bp  
from routes.facturas_route import facturas_bp
from routes.usuarios_route import usuarios_bp
from routes.solicitudes_route import solicitud_bp
from routes.desembolsos_route import desembolsos_bp
from routes.permisos_route import permisos_bp
from routes.web_service import wsFactoraje_bp
from routes.proveedores_route import proveedor_bp
# Cors
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Habilitar CORS para toda la API
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Registrar comandos y blueprints
    init_app(app)
    app.register_blueprint(email_bp, url_prefix='/api/email')
    app.register_blueprint(facturas_bp, url_prefix='/api/factura')
    app.register_blueprint(usuarios_bp, url_prefix='/api/usuario')
    app.register_blueprint(solicitud_bp, url_prefix='/api/solicitud')
    app.register_blueprint(desembolsos_bp, url_prefix='/api/desembolso')
    app.register_blueprint(permisos_bp, url_prefix='/api/permiso')
    app.register_blueprint(wsFactoraje_bp, url_prefix='/api/wsFactoraje')
    app.register_blueprint(proveedor_bp, url_prefix='/api/proveedor')

    return app

if __name__ == '__main__':
    app = create_app()  
    print(app.url_map)
    app.run(debug=True)
