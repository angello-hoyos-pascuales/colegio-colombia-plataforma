from flask import Flask
from config import Config
from extensions import db, login_manager, csrf
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Inicializar extensiones con app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'main.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Crear directorio de uploads si no existe
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Importar modelos
    from models import Usuario, Curso, Asignatura, Tarea, Calificacion, Horario, NotificacionReemplazo
    
    # Función de carga de usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))
    
    # Hacer csrf_token disponible en todos los templates
    @app.context_processor
    def inject_csrf_token():
        from flask_wtf.csrf import generate_csrf
        return dict(csrf_token=generate_csrf())
    
    # Hacer datetime disponible como 'moment' en los templates
    @app.context_processor
    def inject_moment():
        from datetime import datetime
        return dict(moment=lambda: datetime.now())
    
    # Filtro personalizado nl2br para convertir saltos de línea en <br>
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convierte saltos de línea en etiquetas <br>"""
        if not text:
            return text
        from markupsafe import Markup
        import re
        # Convertir \n y \r\n en <br>
        result = re.sub(r'\r\n|\r|\n', '<br>', str(text))
        return Markup(result)
    
    # Registrar blueprints
    from routes.main_routes import main_bp
    from routes.admin_routes import admin_bp
    from routes.profesor_routes import profesor_bp
    from routes.estudiante_routes import estudiante_bp
    from routes.horario_routes import horario_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(profesor_bp, url_prefix='/profesor')
    app.register_blueprint(estudiante_bp, url_prefix='/estudiante')
    app.register_blueprint(horario_bp, url_prefix='/horario')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    print("🌐 Servidor disponible en: http://127.0.0.1:8000")
    print("🔑 Admin: admin@colegiocolombia.edu.co / admin123")
    app.run(debug=True, host='127.0.0.1', port=8000)