import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'colegio-colombia-secret-key-2023'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configuración de archivos subidos
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB máximo
    ALLOWED_EXTENSIONS = {'pdf', 'docx', 'doc', 'txt'}
    
    # Configuración de sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    
    # Configuración específica del colegio
    COLEGIO_NOMBRE = "Colegio Colombia"
    GRADOS_DISPONIBLES = ['6º', '7º', '8º', '9º', '10º', '11º']
    PERIODOS_ACADEMICOS = ['Primer Periodo', 'Segundo Periodo', 'Tercer Periodo', 'Cuarto Periodo']
    
    # Horarios de clases (formato 24h)
    HORAS_CLASES = [
        ('07:00', '07:50'),
        ('07:50', '08:40'),
        ('08:40', '09:30'),
        ('09:50', '10:40'),  # Descanso de 20 min
        ('10:40', '11:30'),
        ('11:30', '12:20'),
        ('13:20', '14:10'),  # Almuerzo de 1h
        ('14:10', '15:00'),
        ('15:00', '15:50')
    ]