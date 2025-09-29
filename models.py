from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from extensions import db

# Tabla de asociación para la relación muchos a muchos entre Usuario y Curso
usuario_curso = db.Table('usuario_curso',
    db.Column('usuario_id', db.Integer, db.ForeignKey('usuario.id'), primary_key=True),
    db.Column('curso_id', db.Integer, db.ForeignKey('curso.id'), primary_key=True)
)

class Usuario(UserMixin, db.Model):
    """Modelo para usuarios del sistema (Administrador, Profesor, Estudiante)"""
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    tipo_documento = db.Column(db.String(10), nullable=False)  # T.I. o C.C.
    numero_documento = db.Column(db.String(20), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.String(200))
    fecha_nacimiento = db.Column(db.Date)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, profesor, estudiante
    materia_especialidad = db.Column(db.String(100))  # Para profesores: materia que enseñan
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    cursos = db.relationship('Curso', secondary=usuario_curso, backref=db.backref('usuarios', lazy='dynamic'))
    tareas_creadas = db.relationship('Tarea', backref='creador', lazy='dynamic', foreign_keys='Tarea.profesor_id')
    calificaciones = db.relationship('Calificacion', backref='estudiante', lazy='dynamic')
    horarios = db.relationship('Horario', backref='profesor', lazy='dynamic', foreign_keys='Horario.profesor_id')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"
    
    @property
    def es_admin(self):
        return self.role == 'admin'
    
    @property
    def es_profesor(self):
        return self.role == 'profesor'
    
    @property
    def es_estudiante(self):
        return self.role == 'estudiante'
    
    @property
    def curso(self):
        """Devuelve el curso principal del estudiante"""
        if self.es_estudiante and self.cursos:
            return self.cursos[0]  # Los estudiantes tienen un solo curso
        return None
    
    def __repr__(self):
        return f'<Usuario {self.nombre_completo}>'

class Curso(db.Model):
    """Modelo para cursos/grados del colegio"""
    id = db.Column(db.Integer, primary_key=True)
    grado = db.Column(db.String(10), nullable=False)  # 6º, 7º, 8º, 9º, 10º, 11º
    seccion = db.Column(db.String(5), nullable=False)  # A, B, C, etc.
    año_academico = db.Column(db.Integer, nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    asignaturas = db.relationship('Asignatura', backref='curso', lazy='dynamic')
    horarios = db.relationship('Horario', backref='curso', lazy='dynamic')
    
    @property
    def nombre_completo(self):
        return f"{self.grado}{self.seccion}"
    
    @property
    def nombre(self):
        """Alias para compatibilidad con templates"""
        return self.grado
    
    @property
    def año(self):
        """Alias para compatibilidad con templates"""
        return self.año_academico
    
    @property
    def director_grupo(self):
        """Obtiene el director de grupo (profesor principal del curso)"""
        # Por ahora retornamos None, pero se puede implementar la lógica
        # para buscar al profesor asignado como director de grupo
        return None
    
    @property
    def estudiantes(self):
        return self.usuarios.filter_by(role='estudiante')
    
    def __repr__(self):
        return f'<Curso {self.nombre_completo} - {self.año_academico}>'

class Asignatura(db.Model):
    """Modelo para asignaturas/materias"""
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    activa = db.Column(db.Boolean, default=True)
    
    # Relaciones
    profesor = db.relationship('Usuario', backref='asignaturas_enseñadas')
    tareas = db.relationship('Tarea', backref='asignatura', lazy='dynamic')
    horarios = db.relationship('Horario', backref='asignatura', lazy='dynamic')
    
    def __repr__(self):
        return f'<Asignatura {self.nombre}>'

class Tarea(db.Model):
    """Modelo para tareas asignadas por profesores"""
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_entrega = db.Column(db.DateTime, nullable=False)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.id'), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    activa = db.Column(db.Boolean, default=True)
    archivo_adjunto = db.Column(db.String(255))  # Ruta del archivo
    
    # Relaciones
    calificaciones = db.relationship('Calificacion', backref='tarea', lazy='dynamic')
    
    @property
    def esta_vencida(self):
        return datetime.utcnow() > self.fecha_entrega
    
    def __repr__(self):
        return f'<Tarea {self.titulo}>'

class Calificacion(db.Model):
    """Modelo para calificaciones de estudiantes"""
    id = db.Column(db.Integer, primary_key=True)
    estudiante_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    tarea_id = db.Column(db.Integer, db.ForeignKey('tarea.id'), nullable=False)
    nota = db.Column(db.Float, nullable=False)  # Nota de 0.0 a 5.0
    comentarios = db.Column(db.Text)
    fecha_calificacion = db.Column(db.DateTime, default=datetime.utcnow)
    archivo_entrega = db.Column(db.String(255))  # Archivo entregado por el estudiante
    periodo = db.Column(db.String(50), nullable=False)  # Periodo académico
    
    def __repr__(self):
        return f'<Calificacion {self.nota}>'

class Horario(db.Model):
    """Modelo para horarios de clases"""
    id = db.Column(db.Integer, primary_key=True)
    dia_semana = db.Column(db.Integer, nullable=False)  # 0=Lunes, 1=Martes, ..., 4=Viernes
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('curso.id'), nullable=False)
    asignatura_id = db.Column(db.Integer, db.ForeignKey('asignatura.id'), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    aula = db.Column(db.String(20))
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    notificaciones_reemplazo = db.relationship('NotificacionReemplazo', backref='horario_original', lazy='dynamic')
    
    @property
    def dia_nombre(self):
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        return dias[self.dia_semana]
    
    def __repr__(self):
        return f'<Horario {self.dia_nombre} {self.hora_inicio}-{self.hora_fin}>'

class NotificacionReemplazo(db.Model):
    """Modelo para notificaciones del sistema de reemplazo de profesores"""
    id = db.Column(db.Integer, primary_key=True)
    horario_id = db.Column(db.Integer, db.ForeignKey('horario.id'), nullable=False)
    profesor_ausente_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    profesor_reemplazo_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    fecha_ausencia = db.Column(db.Date, nullable=False)
    estado = db.Column(db.String(20), default='pendiente')  # pendiente, confirmado, rechazado
    mensaje = db.Column(db.Text)
    fecha_notificacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_respuesta = db.Column(db.DateTime)
    
    # Relaciones
    profesor_ausente = db.relationship('Usuario', foreign_keys=[profesor_ausente_id], backref='ausencias_reportadas')
    profesor_reemplazo = db.relationship('Usuario', foreign_keys=[profesor_reemplazo_id])
    
    @property
    def esta_pendiente(self):
        return self.estado == 'pendiente'
    
    @property
    def esta_confirmado(self):
        return self.estado == 'confirmado'
    
    def __repr__(self):
        return f'<NotificacionReemplazo {self.fecha_ausencia}>'