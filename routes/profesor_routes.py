from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from models import Usuario, Curso, Asignatura, Tarea, Calificacion, NotificacionReemplazo, usuario_curso
from forms import TareaForm, CalificacionForm, RespuestaReemplazoForm
from extensions import db
from datetime import datetime
import os

profesor_bp = Blueprint('profesor', __name__)

def profesor_required(f):
    """Decorador para requerir permisos de profesor"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.es_profesor:
            flash('Acceso denegado. Se requieren permisos de profesor.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@profesor_bp.route('/dashboard')
@login_required
@profesor_required
def dashboard():
    """Dashboard del profesor"""
    # Asignaturas que enseña el profesor
    asignaturas = current_user.asignaturas_enseñadas
    
    # Tareas creadas por el profesor
    tareas_activas = Tarea.query.filter_by(profesor_id=current_user.id, activa=True).count()
    
    # Tareas pendientes de calificar
    tareas_pendientes = db.session.query(Tarea).join(Calificacion, Tarea.id == Calificacion.tarea_id, isouter=True).filter(
        Tarea.profesor_id == current_user.id,
        Tarea.activa == True,
        Calificacion.id == None
    ).count()
    
    # Contar estudiantes totales en cursos del profesor
    estudiantes_total = db.session.query(Usuario).join(usuario_curso).join(Curso).join(Asignatura).filter(
        Asignatura.profesor_id == current_user.id,
        Usuario.role == 'estudiante',
        Usuario.activo == True
    ).distinct().count()
    
    # Clases del día de hoy (simulado)
    from datetime import date, datetime
    today = date.today()
    clases_hoy = 3  # Simulado - en implementación real sería calculado desde Horario
    
    # Notificaciones de reemplazo para el profesor
    notificaciones_reemplazo = NotificacionReemplazo.query.filter_by(
        profesor_reemplazo_id=current_user.id,
        estado='pendiente'
    ).count()
    
    # Notificaciones de reemplazo pendientes
    notificaciones_reemplazo = NotificacionReemplazo.query.filter_by(
        profesor_reemplazo_id=current_user.id,
        estado='pendiente'
    ).all()
    
    # Fecha y hora actual
    fecha_actual = datetime.now()
    
    return render_template('profesor/dashboard.html',
                         asignaturas=asignaturas,
                         tareas_activas=tareas_activas,
                         tareas_pendientes=tareas_pendientes,
                         estudiantes_total=estudiantes_total,
                         clases_hoy=clases_hoy,
                         notificaciones_reemplazo=notificaciones_reemplazo,
                         fecha_actual=fecha_actual)

@profesor_bp.route('/tareas')
@login_required
@profesor_required
def tareas():
    """Listar tareas del profesor"""
    page = request.args.get('page', 1, type=int)
    tareas = Tarea.query.filter_by(profesor_id=current_user.id, activa=True).order_by(
        Tarea.fecha_entrega.desc()).paginate(page=page, per_page=10, error_out=False)
    
    return render_template('profesor/tareas.html', tareas=tareas)

@profesor_bp.route('/tarea/nueva', methods=['GET', 'POST'])
@profesor_bp.route('/nueva_tarea', methods=['GET', 'POST'])
@login_required
@profesor_required
def nueva_tarea():
    """Crear nueva tarea"""
    form = TareaForm()
    # Cargar asignaturas del profesor
    form.asignatura_id.choices = [(a.id, f"{a.nombre} - {a.curso.nombre_completo}") 
                                  for a in current_user.asignaturas_enseñadas]
    
    if form.validate_on_submit():
        tarea = Tarea(
            titulo=form.titulo.data,
            descripcion=form.descripcion.data,
            fecha_entrega=datetime.combine(form.fecha_entrega.data, datetime.min.time()),
            asignatura_id=form.asignatura_id.data,
            profesor_id=current_user.id
        )
        
        # Guardar archivo adjunto si se proporciona
        if form.archivo_adjunto.data:
            filename = secure_filename(form.archivo_adjunto.data.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            filename = timestamp + filename
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'tareas', filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            form.archivo_adjunto.data.save(filepath)
            tarea.archivo_adjunto = f'tareas/{filename}'
        
        db.session.add(tarea)
        db.session.commit()
        
        flash(f'Tarea "{tarea.titulo}" creada correctamente', 'success')
        return redirect(url_for('profesor.tareas'))
    
    return render_template('profesor/tarea_form.html', form=form, title='Nueva Tarea')

@profesor_bp.route('/tarea/<int:id>/calificar')
@login_required
@profesor_required
def calificar_tarea(id):
    """Ver entregas de una tarea para calificar"""
    tarea = Tarea.query.filter_by(id=id, profesor_id=current_user.id).first_or_404()
    
    # Obtener estudiantes del curso de la asignatura
    estudiantes = tarea.asignatura.curso.estudiantes.all()
    
    # Obtener calificaciones existentes
    calificaciones = {c.estudiante_id: c for c in tarea.calificaciones}
    
    return render_template('profesor/calificar_tarea.html', 
                         tarea=tarea, 
                         estudiantes=estudiantes,
                         calificaciones=calificaciones)

@profesor_bp.route('/calificacion/<int:tarea_id>/<int:estudiante_id>', methods=['GET', 'POST'])
@login_required
@profesor_required
def calificacion_individual(tarea_id, estudiante_id):
    """Calificar tarea de un estudiante específico"""
    tarea = Tarea.query.filter_by(id=tarea_id, profesor_id=current_user.id).first_or_404()
    estudiante = Usuario.query.filter_by(id=estudiante_id, role='estudiante').first_or_404()
    
    # Verificar que el estudiante esté en el curso de la asignatura
    if estudiante not in tarea.asignatura.curso.estudiantes:
        flash('El estudiante no pertenece al curso de esta asignatura', 'error')
        return redirect(url_for('profesor.calificar_tarea', id=tarea_id))
    
    # Buscar calificación existente
    calificacion = Calificacion.query.filter_by(tarea_id=tarea_id, estudiante_id=estudiante_id).first()
    
    form = CalificacionForm(obj=calificacion)
    
    if form.validate_on_submit():
        if calificacion:
            # Actualizar calificación existente
            calificacion.nota = form.nota.data
            calificacion.comentarios = form.comentarios.data
            calificacion.periodo = form.periodo.data
            calificacion.fecha_calificacion = datetime.utcnow()
        else:
            # Crear nueva calificación
            calificacion = Calificacion(
                estudiante_id=estudiante_id,
                tarea_id=tarea_id,
                nota=form.nota.data,
                comentarios=form.comentarios.data,
                periodo=form.periodo.data
            )
            db.session.add(calificacion)
        
        db.session.commit()
        flash(f'Calificación guardada para {estudiante.nombre_completo}', 'success')
        return redirect(url_for('profesor.calificar_tarea', id=tarea_id))
    
    return render_template('profesor/calificacion_form.html', 
                         form=form, 
                         tarea=tarea, 
                         estudiante=estudiante,
                         calificacion=calificacion)

@profesor_bp.route('/estudiantes')
@login_required
@profesor_required
def estudiantes():
    """Ver lista de estudiantes de las asignaturas del profesor"""
    # Obtener asignaturas del profesor
    asignaturas_profesor = current_user.asignaturas_enseñadas
    cursos_ids = [a.curso_id for a in asignaturas_profesor]
    
    if not cursos_ids:
        # Si no hay cursos asignados, devolver lista vacía
        return render_template('profesor/estudiantes.html', 
                             estudiantes=[],
                             cursos_profesor=[])
    
    # Obtener estudiantes de los cursos del profesor
    estudiantes_query = Usuario.query.join(usuario_curso).filter(
        usuario_curso.c.curso_id.in_(cursos_ids),
        Usuario.role == 'estudiante',
        Usuario.activo == True
    ).distinct().order_by(Usuario.apellidos, Usuario.nombres).all()
    
    # Crear estructura de datos simplificada pero compatible
    estudiantes_con_info = []
    cursos_profesor = set()
    
    for estudiante in estudiantes_query:
        # Obtener primer curso del estudiante que coincida con los del profesor
        curso_estudiante = None
        for c in estudiante.cursos:
            if c.id in cursos_ids:
                curso_estudiante = c
                break
        
        if curso_estudiante:
            # Obtener asignaturas del profesor para este curso
            asignaturas_curso = [a.nombre for a in asignaturas_profesor if a.curso_id == curso_estudiante.id]
            
            # Crear objeto de información simplificado
            curso_info = {
                'curso': curso_estudiante.nombre_completo,
                'asignaturas': asignaturas_curso,
                'tareas_entregadas': 0,  # Se calculará después si es necesario
                'promedio': 0.0,
                'calificaciones': 0
            }
            
            # Crear tupla (estudiante, curso_info)
            estudiantes_con_info.append((estudiante, curso_info))
            cursos_profesor.add(curso_estudiante.nombre_completo)
    
    return render_template('profesor/estudiantes.html', 
                         estudiantes=estudiantes_con_info,
                         cursos_profesor=sorted(list(cursos_profesor)))

@profesor_bp.route('/notificaciones')
@login_required
@profesor_required
def notificaciones():
    """Ver notificaciones de reemplazo"""
    notificaciones = NotificacionReemplazo.query.filter_by(
        profesor_reemplazo_id=current_user.id
    ).order_by(NotificacionReemplazo.fecha_notificacion.desc()).all()
    
    return render_template('profesor/notificaciones.html', notificaciones=notificaciones)

@profesor_bp.route('/responder_reemplazo/<int:id>', methods=['GET', 'POST'])
@login_required
@profesor_required
def responder_reemplazo(id):
    """Responder a una solicitud de reemplazo"""
    notificacion = NotificacionReemplazo.query.filter_by(
        id=id, 
        profesor_reemplazo_id=current_user.id,
        estado='pendiente'
    ).first_or_404()
    
    form = RespuestaReemplazoForm()
    
    if form.validate_on_submit():
        if form.aceptar.data:
            notificacion.estado = 'confirmado'
            flash('Has aceptado realizar el reemplazo', 'success')
        else:
            notificacion.estado = 'rechazado'
            flash('Has rechazado la solicitud de reemplazo', 'info')
        
        notificacion.fecha_respuesta = datetime.utcnow()
        if form.mensaje.data:
            notificacion.mensaje += f"\n\nRespuesta del profesor: {form.mensaje.data}"
        
        db.session.commit()
        return redirect(url_for('profesor.notificaciones'))
    
    return render_template('profesor/respuesta_reemplazo.html', 
                         form=form, 
                         notificacion=notificacion)

@profesor_bp.route('/estudiante/<int:estudiante_id>/calificaciones')
@login_required
@profesor_required
def ver_calificaciones_estudiante(estudiante_id):
    """Ver todas las calificaciones de un estudiante"""
    estudiante = Usuario.query.filter_by(id=estudiante_id, role='estudiante').first_or_404()
    
    # Verificar que el profesor enseña a este estudiante
    asignaturas_profesor = current_user.asignaturas_enseñadas
    cursos_profesor = [asig.curso for asig in asignaturas_profesor]
    
    if estudiante.curso not in cursos_profesor:
        flash('No tienes permisos para ver las calificaciones de este estudiante', 'error')
        return redirect(url_for('profesor.estudiantes'))
    
    # Obtener calificaciones del estudiante en asignaturas del profesor
    calificaciones = Calificacion.query.join(Tarea).join(Asignatura).filter(
        Calificacion.estudiante_id == estudiante_id,
        Asignatura.profesor_id == current_user.id
    ).order_by(Calificacion.fecha_calificacion.desc()).all()
    
    return render_template('profesor/calificaciones_estudiante.html',
                         estudiante=estudiante,
                         calificaciones=calificaciones)

@profesor_bp.route('/estudiante/<int:estudiante_id>/contactar')
@login_required
@profesor_required
def contactar_estudiante(estudiante_id):
    """Contactar a un estudiante (funcionalidad básica)"""
    estudiante = Usuario.query.filter_by(id=estudiante_id, role='estudiante').first_or_404()
    
    # Verificar que el profesor enseña a este estudiante
    asignaturas_profesor = current_user.asignaturas_enseñadas
    cursos_profesor = [asig.curso for asig in asignaturas_profesor]
    
    if estudiante.curso not in cursos_profesor:
        flash('No tienes permisos para contactar a este estudiante', 'error')
        return redirect(url_for('profesor.estudiantes'))
    
    # Por ahora, solo mostrar información de contacto
    flash(f'Funcionalidad de contacto en desarrollo. Email del estudiante: {estudiante.email}', 'info')
    return redirect(url_for('profesor.estudiantes'))