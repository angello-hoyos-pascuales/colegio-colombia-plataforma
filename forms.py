from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, IntegerField, FloatField, BooleanField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, EqualTo
from datetime import datetime, date

class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    email = StringField('Correo Electrónico', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')

class RegistroUsuarioForm(FlaskForm):
    """Formulario para registro de usuarios"""
    nombres = StringField('Nombres', validators=[DataRequired(), Length(min=2, max=100)])
    apellidos = StringField('Apellidos', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    tipo_documento = SelectField('Tipo de Documento', 
                                choices=[('T.I.', 'Tarjeta de Identidad'), ('C.C.', 'Cédula de Ciudadanía')],
                                validators=[DataRequired()])
    numero_documento = StringField('Número de Documento', validators=[DataRequired(), Length(min=5, max=20)])
    telefono = StringField('Teléfono', validators=[Optional(), Length(max=15)])
    direccion = StringField('Dirección', validators=[Optional(), Length(max=200)])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[Optional()])
    role = SelectField('Rol', 
                     choices=[('estudiante', 'Estudiante'), ('profesor', 'Profesor'), ('admin', 'Administrador')],
                     validators=[DataRequired()])
    
    # Campos específicos para estudiantes
    curso_id = SelectField('Curso', coerce=int, validators=[Optional()])
    
    # Campos específicos para profesores  
    materia_especialidad = SelectField('Materia de Especialidad', 
                                     choices=[('', 'Seleccionar materia...'),
                                             ('Matemáticas', 'Matemáticas'), 
                                             ('Español', 'Español'),
                                             ('Ciencias Naturales', 'Ciencias Naturales'),
                                             ('Biología', 'Biología'),
                                             ('Química', 'Química'),
                                             ('Física', 'Física'),
                                             ('Sociales', 'Sociales'), 
                                             ('Inglés', 'Inglés'),
                                             ('Educación Física', 'Educación Física'),
                                             ('Artística', 'Artística'),
                                             ('Ética', 'Ética'),
                                             ('Religión', 'Religión'),
                                             ('Filosofía', 'Filosofía'),
                                             ('Economía', 'Economía')],
                                     validators=[Optional()])
    
    password = PasswordField('Contraseña', validators=[Optional(), Length(min=6)])
    password2 = PasswordField('Confirmar Contraseña', 
                             validators=[Optional(), EqualTo('password', message='Las contraseñas deben coincidir')])
    activo = BooleanField('Usuario Activo', default=True)
    submit = SubmitField('Guardar Usuario')

class CursoForm(FlaskForm):
    """Formulario para crear/editar cursos"""
    grado = SelectField('Grado', 
                       choices=[('6º', '6º'), ('7º', '7º'), ('8º', '8º'), ('9º', '9º'), ('10º', '10º'), ('11º', '11º')],
                       validators=[DataRequired()])
    seccion = SelectField('Sección', 
                         choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
                         validators=[DataRequired()])
    año_academico = IntegerField('Año Académico', 
                                validators=[DataRequired(), NumberRange(min=2020, max=2030)],
                                default=datetime.now().year)
    nombre = StringField('Nombre del Curso', validators=[Optional(), Length(max=50)])
    activo = BooleanField('Curso Activo', default=True)
    submit = SubmitField('Guardar Curso')

class AsignaturaForm(FlaskForm):
    """Formulario para crear/editar asignaturas"""
    materia = SelectField('Materia', 
                         choices=[('Matemáticas', 'Matemáticas'), ('Español', 'Español'), 
                                 ('Ciencias', 'Ciencias'), ('Sociales', 'Sociales'),
                                 ('Inglés', 'Inglés'), ('Educación Física', 'Educación Física')],
                         validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[Optional(), Length(max=500)])
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    profesor_id = SelectField('Profesor', coerce=int, validators=[DataRequired()])
    activa = BooleanField('Asignatura Activa', default=True)
    submit = SubmitField('Guardar Asignatura')

class TareaForm(FlaskForm):
    """Formulario para crear/editar tareas"""
    titulo = StringField('Título', validators=[DataRequired(), Length(min=3, max=200)])
    descripcion = TextAreaField('Descripción', validators=[DataRequired(), Length(min=10, max=1000)])
    fecha_entrega = DateField('Fecha de Entrega', validators=[DataRequired()])
    asignatura_id = SelectField('Asignatura', coerce=int, validators=[DataRequired()])
    archivo_adjunto = FileField('Archivo Adjunto', validators=[
        Optional(), FileAllowed(['pdf', 'docx', 'doc', 'txt'], 'Solo se permiten archivos PDF, DOCX, DOC y TXT')
    ])
    submit = SubmitField('Crear Tarea')

class CalificacionForm(FlaskForm):
    """Formulario para calificar tareas"""
    nota = FloatField('Nota', validators=[DataRequired(), NumberRange(min=0.0, max=5.0, 
                                         message='La nota debe estar entre 0.0 y 5.0')])
    comentarios = TextAreaField('Comentarios', validators=[Optional(), Length(max=500)])
    periodo = SelectField('Periodo', 
                         choices=[('Primer Periodo', 'Primer Periodo'), 
                                 ('Segundo Periodo', 'Segundo Periodo'),
                                 ('Tercer Periodo', 'Tercer Periodo'),
                                 ('Cuarto Periodo', 'Cuarto Periodo')],
                         validators=[DataRequired()])
    submit = SubmitField('Guardar Calificación')

class EntregaTareaForm(FlaskForm):
    """Formulario para que estudiantes entreguen tareas"""
    archivo_entrega = FileField('Archivo de Entrega', validators=[
        DataRequired(), FileAllowed(['pdf', 'docx', 'doc', 'txt'], 
                                   'Solo se permiten archivos PDF, DOCX, DOC y TXT')
    ])
    comentarios = TextAreaField('Comentarios', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Entregar Tarea')

class HorarioForm(FlaskForm):
    """Formulario para crear/editar horarios"""
    dia_semana = SelectField('Día de la Semana', 
                            choices=[(0, 'Lunes'), (1, 'Martes'), (2, 'Miércoles'), 
                                   (3, 'Jueves'), (4, 'Viernes')],
                            coerce=int, validators=[DataRequired()])
    hora_inicio = TimeField('Hora de Inicio', validators=[DataRequired()])
    hora_fin = TimeField('Hora de Fin', validators=[DataRequired()])
    curso_id = SelectField('Curso', coerce=int, validators=[DataRequired()])
    asignatura_id = SelectField('Asignatura', coerce=int, validators=[DataRequired()])
    profesor_id = SelectField('Profesor', coerce=int, validators=[DataRequired()])
    aula = StringField('Aula', validators=[Optional(), Length(max=20)])
    submit = SubmitField('Guardar Horario')

class AusenciaProfesorForm(FlaskForm):
    """Formulario para reportar ausencia de profesor"""
    profesor_id = SelectField('Profesor Ausente', coerce=int, validators=[DataRequired()])
    fecha_ausencia = DateField('Fecha de Ausencia', validators=[DataRequired()], default=date.today)
    motivo = TextAreaField('Motivo de la Ausencia', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Reportar Ausencia')

class RespuestaReemplazoForm(FlaskForm):
    """Formulario para que profesores respondan a solicitudes de reemplazo"""
    aceptar = BooleanField('Acepto realizar el reemplazo')
    mensaje = TextAreaField('Mensaje', validators=[Optional(), Length(max=300)])
    submit = SubmitField('Enviar Respuesta')

class FiltroProfesorForm(FlaskForm):
    """Formulario para filtrar profesores por materia"""
    materia_filtro = SelectField('Filtrar por Materia', 
                                choices=[('', 'Todas las materias'),
                                        ('Matemáticas', 'Matemáticas'), 
                                        ('Español', 'Español'),
                                        ('Ciencias Naturales', 'Ciencias Naturales'),
                                        ('Biología', 'Biología'),
                                        ('Química', 'Química'),
                                        ('Física', 'Física'),
                                        ('Sociales', 'Sociales'), 
                                        ('Inglés', 'Inglés'),
                                        ('Educación Física', 'Educación Física'),
                                        ('Artística', 'Artística'),
                                        ('Ética', 'Ética'),
                                        ('Religión', 'Religión'),
                                        ('Filosofía', 'Filosofía'),
                                        ('Economía', 'Economía')],
                                validators=[Optional()])
    submit = SubmitField('Filtrar')