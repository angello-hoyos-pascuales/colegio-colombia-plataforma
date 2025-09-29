from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from functools import wraps
from werkzeug.utils import secure_filename
from models import Usuario, Curso, Asignatura, Tarea, Calificacion, Horario, usuario_curso
from forms import EntregaTareaForm
from extensions import db
from datetime import datetime
import os

estudiante_bp = Blueprint('estudiante', __name__)

def estudiante_required(f):
    """Decorador para requerir permisos de estudiante"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.es_estudiante:
            flash('Acceso denegado. Se requieren permisos de estudiante.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@estudiante_bp.route('/dashboard')
@login_required
@estudiante_required
def dashboard():
    """Dashboard del estudiante"""
    # Obtener cursos del estudiante
    cursos = current_user.cursos
    
    # Tareas pendientes
    tareas_pendientes = db.session.query(Tarea).join(Asignatura).join(Curso).join(usuario_curso).filter(
        usuario_curso.c.usuario_id == current_user.id,
        Tarea.activa == True,
        Tarea.fecha_entrega > datetime.utcnow()
    ).order_by(Tarea.fecha_entrega).limit(5).all()
    
    # Tareas vencidas sin entregar
    tareas_vencidas = db.session.query(Tarea).join(Asignatura).join(Curso).join(usuario_curso).outerjoin(
        Calificacion, (Calificacion.tarea_id == Tarea.id) & (Calificacion.estudiante_id == current_user.id)
    ).filter(
        usuario_curso.c.usuario_id == current_user.id,
        Tarea.activa == True,
        Tarea.fecha_entrega < datetime.utcnow(),
        Calificacion.id == None
    ).count()
    
    # Calcular promedio general
    calificaciones = Calificacion.query.filter_by(estudiante_id=current_user.id).all()
    promedio_general = sum(c.nota for c in calificaciones) / len(calificaciones) if calificaciones else 0.0
    
    # Clases del día de hoy (simulado)
    clases_hoy = 4  # Simulado
    
    # Calificaciones recientes
    calificaciones_recientes = Calificacion.query.filter_by(
        estudiante_id=current_user.id
    ).order_by(Calificacion.fecha_calificacion.desc()).limit(5).all()
    
    return render_template('estudiante/dashboard.html',
                         cursos=cursos,
                         tareas_pendientes=tareas_pendientes,
                         tareas_vencidas=tareas_vencidas,
                         calificaciones_recientes=calificaciones_recientes,
                         promedio_general=promedio_general,
                         clases_hoy=clases_hoy)

@estudiante_bp.route('/tareas')
@login_required
@estudiante_required
def tareas():
    """Ver todas las tareas del estudiante"""
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todas')
    
    # Query base para tareas del estudiante
    query = db.session.query(Tarea).join(Asignatura).join(Curso).join(usuario_curso).filter(
        usuario_curso.c.usuario_id == current_user.id,
        Tarea.activa == True
    )
    
    # Filtrar por estado
    if estado == 'pendientes':
        query = query.filter(Tarea.fecha_entrega > datetime.utcnow())
    elif estado == 'vencidas':
        query = query.filter(Tarea.fecha_entrega < datetime.utcnow())
    
    tareas = query.order_by(Tarea.fecha_entrega.desc()).paginate(
        page=page, per_page=10, error_out=False)
    
    # Obtener calificaciones del estudiante para estas tareas
    tareas_ids = [t.id for t in tareas.items]
    calificaciones = {c.tarea_id: c for c in Calificacion.query.filter(
        Calificacion.estudiante_id == current_user.id,
        Calificacion.tarea_id.in_(tareas_ids)
    ).all()}
    
    return render_template('estudiante/tareas.html', 
                         tareas=tareas, 
                         calificaciones=calificaciones,
                         estado_filtro=estado)

@estudiante_bp.route('/tarea/<int:id>')
@login_required
@estudiante_required
def detalle_tarea(id):
    """Ver detalle de una tarea específica"""
    tarea = db.session.query(Tarea).join(Asignatura).join(Curso).join(usuario_curso).filter(
        Tarea.id == id,
        usuario_curso.c.usuario_id == current_user.id,
        Tarea.activa == True
    ).first_or_404()
    
    # Verificar si ya hay una calificación
    calificacion = Calificacion.query.filter_by(
        tarea_id=id,
        estudiante_id=current_user.id
    ).first()
    
    return render_template('estudiante/detalle_tarea.html', 
                         tarea=tarea, 
                         calificacion=calificacion)

@estudiante_bp.route('/tarea/<int:id>/entregar', methods=['GET', 'POST'])
@login_required
@estudiante_required
def entregar_tarea(id):
    """Entregar una tarea"""
    tarea = db.session.query(Tarea).join(Asignatura).join(Curso).join(usuario_curso).filter(
        Tarea.id == id,
        usuario_curso.c.usuario_id == current_user.id,
        Tarea.activa == True
    ).first_or_404()
    
    # Verificar si ya existe una calificación (ya fue entregada)
    calificacion_existente = Calificacion.query.filter_by(
        tarea_id=id,
        estudiante_id=current_user.id
    ).first()
    
    if calificacion_existente and calificacion_existente.archivo_entrega:
        flash('Ya has entregado esta tarea', 'info')
        return redirect(url_for('estudiante.detalle_tarea', id=id))
    
    form = EntregaTareaForm()
    
    if form.validate_on_submit():
        # Guardar archivo de entrega
        filename = secure_filename(form.archivo_entrega.data.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = f"{current_user.numero_documento}_{timestamp}{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'entregas', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        form.archivo_entrega.data.save(filepath)
        
        if calificacion_existente:
            # Actualizar entrega existente
            calificacion_existente.archivo_entrega = f'entregas/{filename}'
            if form.comentarios.data:
                calificacion_existente.comentarios = form.comentarios.data
        else:
            # Crear nueva entrega (sin nota aún)
            calificacion = Calificacion(
                estudiante_id=current_user.id,
                tarea_id=id,
                nota=0.0,  # Se calificará después
                archivo_entrega=f'entregas/{filename}',
                comentarios=form.comentarios.data,
                periodo='Primer Periodo'  # Default, se actualizará al calificar
            )
            db.session.add(calificacion)
        
        db.session.commit()
        flash('Tarea entregada correctamente', 'success')
        return redirect(url_for('estudiante.detalle_tarea', id=id))
    
    return render_template('estudiante/entregar_tarea.html', 
                         form=form, 
                         tarea=tarea)

@estudiante_bp.route('/calificaciones')
@login_required
@estudiante_required
def calificaciones():
    """Ver todas las calificaciones del estudiante"""
    page = request.args.get('page', 1, type=int)
    periodo = request.args.get('periodo', 'todos')
    
    query = Calificacion.query.filter_by(estudiante_id=current_user.id)
    
    if periodo != 'todos':
        query = query.filter_by(periodo=periodo)
    
    calificaciones = query.order_by(Calificacion.fecha_calificacion.desc()).paginate(
        page=page, per_page=15, error_out=False)
    
    # Calcular promedio por periodo
    promedios = {}
    for p in ['Primer Periodo', 'Segundo Periodo', 'Tercer Periodo', 'Cuarto Periodo']:
        notas = [c.nota for c in Calificacion.query.filter_by(
            estudiante_id=current_user.id,
            periodo=p
        ).all() if c.nota > 0]
        if notas:
            promedios[p] = sum(notas) / len(notas)
    
    return render_template('estudiante/calificaciones.html',
                         calificaciones=calificaciones,
                         promedios=promedios,
                         periodo_filtro=periodo)

@estudiante_bp.route('/horario')
@login_required
@estudiante_required
def horario():
    """Ver horario del estudiante"""
    # Obtener horarios de todos los cursos del estudiante
    horarios = db.session.query(Horario).join(Curso).join(usuario_curso).filter(
        usuario_curso.c.usuario_id == current_user.id,
        Horario.activo == True
    ).order_by(Horario.dia_semana, Horario.hora_inicio).all()
    
    # Organizar horarios por día y hora
    horario_organizado = {}
    for horario in horarios:
        dia = horario.dia_nombre
        if dia not in horario_organizado:
            horario_organizado[dia] = []
        horario_organizado[dia].append(horario)
    
    return render_template('estudiante/horario.html', 
                         horario_organizado=horario_organizado)

@estudiante_bp.route('/perfil')
@login_required
@estudiante_required
def perfil():
    """Ver perfil del estudiante"""
    return render_template('estudiante/perfil.html', usuario=current_user)