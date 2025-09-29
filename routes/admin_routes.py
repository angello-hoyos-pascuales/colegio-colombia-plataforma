from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort, send_file, Response, current_app
from flask_login import login_required, current_user
from functools import wraps
from models import Usuario, Curso, Asignatura, Tarea, Calificacion, Horario, NotificacionReemplazo, usuario_curso
from forms import RegistroUsuarioForm, CursoForm, AsignaturaForm, HorarioForm, AusenciaProfesorForm, FiltroProfesorForm
from extensions import db
from datetime import datetime, date
import os

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('No tienes permisos para acceder a esta sección.', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Dashboard principal del administrador"""
    total_usuarios = Usuario.query.count()
    total_estudiantes = Usuario.query.filter_by(role='estudiante').count()
    total_profesores = Usuario.query.filter_by(role='profesor').count()
    total_cursos = Curso.query.count()
    total_asignaturas = Asignatura.query.count()
    total_tareas = Tarea.query.count()
    
    # Obtener estadísticas recientes
    usuarios_recientes = Usuario.query.order_by(Usuario.id.desc()).limit(5).all()
    ausencias_hoy = NotificacionReemplazo.query.filter(
        NotificacionReemplazo.fecha_ausencia >= datetime.now().date()
    ).count()
    
    # Notificaciones pendientes de reemplazo
    notificaciones_pendientes = NotificacionReemplazo.query.filter(
        NotificacionReemplazo.estado == 'pendiente',
        NotificacionReemplazo.fecha_ausencia >= datetime.now().date()
    ).count()
    
    # Profesores activos disponibles para reemplazo
    profesores_disponibles = Usuario.query.filter(
        Usuario.role == 'profesor',
        Usuario.activo == True
    ).count()
    
    return render_template('admin/dashboard.html', 
                         total_usuarios=total_usuarios,
                         total_estudiantes=total_estudiantes,
                         total_profesores=total_profesores,
                         total_cursos=total_cursos,
                         total_asignaturas=total_asignaturas,
                         total_tareas=total_tareas,
                         usuarios_recientes=usuarios_recientes,
                         ausencias_hoy=ausencias_hoy,
                         notificaciones_pendientes=notificaciones_pendientes,
                         profesores_disponibles=profesores_disponibles)

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios():
    """Listar todos los usuarios con paginación y filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtros
    role_filter = request.args.get('role')
    search = request.args.get('search')
    
    query = Usuario.query
    
    if role_filter and role_filter != 'todos':
        query = query.filter_by(role=role_filter)
    
    if search:
        query = query.filter(
            (Usuario.nombres.contains(search)) |
            (Usuario.apellidos.contains(search)) |
            (Usuario.email.contains(search))
        )
    
    usuarios_paginados = query.order_by(Usuario.apellidos, Usuario.nombres).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/usuarios.html', 
                         usuarios=usuarios_paginados,
                         role_filter=role_filter,
                         search=search)

@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_usuario():
    """Crear nuevo usuario"""
    form = RegistroUsuarioForm()
    
    # Cargar opciones para cursos (solo para estudiantes)
    cursos = Curso.query.order_by(Curso.grado, Curso.seccion).all()
    form.curso_id.choices = [(0, 'Seleccionar curso...')] + [(c.id, f"{c.grado}{c.seccion}") for c in cursos]
    
    if form.validate_on_submit():
        # Verificar si el email ya existe
        existing_user = Usuario.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Ya existe un usuario con ese email.', 'error')
            return render_template('admin/usuario_form.html', form=form)
        
        # Crear nuevo usuario
        usuario = Usuario(
            nombres=form.nombres.data,
            apellidos=form.apellidos.data,
            tipo_documento=form.tipo_documento.data,
            numero_documento=form.numero_documento.data,
            email=form.email.data,
            telefono=form.telefono.data,
            direccion=form.direccion.data,
            role=form.role.data
        )
        
        # Asignar curso si es estudiante
        if form.role.data == 'estudiante' and form.curso_id.data and form.curso_id.data != 0:
            curso = Curso.query.get(form.curso_id.data)
            if curso:
                usuario.cursos.append(curso)
        
        # Asignar materia de especialidad si es profesor
        if form.role.data == 'profesor' and form.materia_especialidad.data:
            usuario.materia_especialidad = form.materia_especialidad.data
        
        # Establecer contraseña por defecto
        if form.role.data == 'estudiante':
            usuario.set_password('estudiante123')
        elif form.role.data == 'profesor':
            usuario.set_password('profesor123')
        else:
            usuario.set_password('admin123')
        
        db.session.add(usuario)
        db.session.commit()
        
        flash(f'Usuario {usuario.nombres} {usuario.apellidos} creado exitosamente.', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, title="Nuevo Usuario")

@admin_bp.route('/usuarios/<int:id>')
@login_required
@admin_required
def ver_usuario(id):
    """Ver detalles de un usuario"""
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    return render_template('admin/usuario_detalle.html', usuario=usuario)

@admin_bp.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_usuario(id):
    """Editar usuario existente"""
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    
    form = RegistroUsuarioForm(obj=usuario)
    
    # Cargar opciones para cursos
    cursos = Curso.query.order_by(Curso.grado, Curso.seccion).all()
    form.curso_id.choices = [(0, 'Seleccionar curso...')] + [(c.id, f"{c.grado}{c.seccion}") for c in cursos]
    
    # Establecer valores actuales
    if usuario.es_estudiante and usuario.cursos:
        form.curso_id.data = usuario.cursos[0].id
    if usuario.materia_especialidad:
        form.materia_especialidad.data = usuario.materia_especialidad
    
    if form.validate_on_submit():
        # Verificar email único (excluyendo el usuario actual)
        existing_user = Usuario.query.filter(
            Usuario.email == form.email.data,
            Usuario.id != id
        ).first()
        
        if existing_user:
            flash('Ya existe otro usuario con ese email.', 'error')
            return render_template('admin/usuario_form.html', form=form, usuario=usuario, title="Editar Usuario")
        
        # Actualizar datos
        usuario.nombres = form.nombres.data
        usuario.apellidos = form.apellidos.data
        usuario.tipo_documento = form.tipo_documento.data
        usuario.numero_documento = form.numero_documento.data
        usuario.email = form.email.data
        usuario.telefono = form.telefono.data
        usuario.direccion = form.direccion.data
        usuario.role = form.role.data
        
        # Actualizar curso si es estudiante
        if form.role.data == 'estudiante' and form.curso_id.data and form.curso_id.data != 0:
            # Limpiar cursos existentes
            usuario.cursos.clear()
            curso = Curso.query.get(form.curso_id.data)
            if curso:
                usuario.cursos.append(curso)
        else:
            # Limpiar cursos si no es estudiante
            usuario.cursos.clear()
        
        # Actualizar materia de especialidad si es profesor
        if form.role.data == 'profesor' and form.materia_especialidad.data:
            usuario.materia_especialidad = form.materia_especialidad.data
        else:
            usuario.materia_especialidad = None
        
        db.session.commit()
        flash(f'Usuario {usuario.nombres} {usuario.apellidos} actualizado exitosamente.', 'success')
        return redirect(url_for('admin.usuarios'))
    
    return render_template('admin/usuario_form.html', form=form, usuario=usuario, title="Editar Usuario")

@admin_bp.route('/usuarios/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_usuario(id):
    """Eliminar un usuario"""
    usuario = db.session.get(Usuario, id)
    if not usuario:
        abort(404)
    
    nombre_completo = f"{usuario.nombres} {usuario.apellidos}"
    db.session.delete(usuario)
    db.session.commit()
    
    flash(f'Usuario {nombre_completo} eliminado exitosamente.', 'success')
    return redirect(url_for('admin.usuarios'))

@admin_bp.route('/cursos')
@login_required
@admin_required
def cursos():
    """Listar todos los cursos"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    cursos_paginados = Curso.query.order_by(Curso.grado, Curso.seccion).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/cursos.html', cursos=cursos_paginados)

@admin_bp.route('/cursos/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def nuevo_curso():
    """Crear nuevo curso"""
    form = CursoForm()
    
    if form.validate_on_submit():
        # Verificar si ya existe el curso con esa combinación
        existing_curso = Curso.query.filter_by(
            grado=form.grado.data,
            seccion=form.seccion.data
        ).first()
        
        if existing_curso:
            flash('Ya existe un curso con ese grado y sección.', 'error')
            return render_template('admin/curso_form.html', form=form)
        
        curso = Curso(
            grado=form.grado.data,
            seccion=form.seccion.data,
            año_academico=form.año_academico.data,
            activo=form.activo.data
        )
        
        db.session.add(curso)
        db.session.commit()
        
        flash(f'Curso {curso.grado}{curso.seccion} creado exitosamente.', 'success')
        return redirect(url_for('admin.cursos'))
    
    return render_template('admin/curso_form.html', form=form, title="Nuevo Curso")

@admin_bp.route('/cursos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_curso(id):
    """Editar curso existente"""
    curso = db.session.get(Curso, id)
    if not curso:
        abort(404)
    
    form = CursoForm(obj=curso)
    
    if form.validate_on_submit():
        # Verificar unicidad excluyendo el curso actual
        existing_curso = Curso.query.filter(
            Curso.grado == form.grado.data,
            Curso.seccion == form.seccion.data,
            Curso.id != id
        ).first()
        
        if existing_curso:
            flash('Ya existe otro curso con ese nombre y sección.', 'error')
            return render_template('admin/curso_form.html', form=form, curso=curso, title="Editar Curso")
        
        curso.grado = form.grado.data
        curso.seccion = form.seccion.data
        curso.descripcion = form.descripcion.data
        curso.activo = form.activo.data
        
        db.session.commit()
        flash(f'Curso {curso.grado}{curso.seccion} actualizado exitosamente.', 'success')
        return redirect(url_for('admin.cursos'))
    
    return render_template('admin/curso_form.html', form=form, curso=curso, title="Editar Curso")

@admin_bp.route('/cursos/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_curso(id):
    """Eliminar un curso"""
    curso = db.session.get(Curso, id)
    if not curso:
        abort(404)
    
    nombre_completo = f"{curso.grado}{curso.seccion}"
    db.session.delete(curso)
    db.session.commit()
    
    flash(f'Curso {nombre_completo} eliminado exitosamente.', 'success')
    return redirect(url_for('admin.cursos'))

@admin_bp.route('/asignaturas')
@login_required
@admin_required
def asignaturas():
    """Listar todas las asignaturas con filtros"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Filtros
    profesor_filter = request.args.get('profesor_id')
    curso_filter = request.args.get('curso_id')
    
    query = Asignatura.query
    
    if profesor_filter:
        query = query.filter_by(profesor_id=profesor_filter)
    
    if curso_filter:
        query = query.filter_by(curso_id=curso_filter)
    
    asignaturas_paginadas = query.order_by(Asignatura.nombre).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Para los filtros
    profesores = Usuario.query.filter_by(role='profesor').order_by(Usuario.apellidos, Usuario.nombres).all()
    cursos = Curso.query.order_by(Curso.grado, Curso.seccion).all()
    
    return render_template('admin/asignaturas.html', 
                         asignaturas=asignaturas_paginadas,
                         profesores=profesores,
                         cursos=cursos,
                         profesor_filter=profesor_filter,
                         curso_filter=curso_filter)

@admin_bp.route('/asignaturas/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def nueva_asignatura():
    """Crear nueva asignatura"""
    form = AsignaturaForm()
    
    # Cargar opciones
    profesores = Usuario.query.filter_by(role='profesor').order_by(Usuario.apellidos, Usuario.nombres).all()
    cursos = Curso.query.order_by(Curso.grado, Curso.seccion).all()
    
    form.profesor_id.choices = [(0, 'Seleccionar profesor...')] + [(p.id, f"{p.nombres} {p.apellidos}") for p in profesores]
    form.curso_id.choices = [(0, 'Seleccionar curso...')] + [(c.id, f"{c.grado}{c.seccion}") for c in cursos]
    
    if form.validate_on_submit():
        # Validar que profesor y curso estén seleccionados
        if form.profesor_id.data == 0:
            flash('Debe seleccionar un profesor válido.', 'error')
            return render_template('admin/asignatura_form.html', form=form, title="Nueva Asignatura")
        
        if form.curso_id.data == 0:
            flash('Debe seleccionar un curso válido.', 'error')
            return render_template('admin/asignatura_form.html', form=form, title="Nueva Asignatura")
        
        asignatura = Asignatura(
            nombre=form.nombre.data,
            descripcion=form.descripcion.data,
            profesor_id=form.profesor_id.data,
            curso_id=form.curso_id.data,
            activa=form.activa.data
        )
        
        db.session.add(asignatura)
        db.session.commit()
        
        flash(f'Asignatura {asignatura.nombre} creada exitosamente.', 'success')
        return redirect(url_for('admin.asignaturas'))
    
    return render_template('admin/asignatura_form.html', form=form, title="Nueva Asignatura")

@admin_bp.route('/asignaturas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def editar_asignatura(id):
    """Editar asignatura existente"""
    asignatura = db.session.get(Asignatura, id)
    if not asignatura:
        abort(404)
    
    form = AsignaturaForm(obj=asignatura)
    
    # Cargar opciones
    profesores = Usuario.query.filter_by(role='profesor').order_by(Usuario.apellidos, Usuario.nombres).all()
    cursos = Curso.query.order_by(Curso.grado, Curso.seccion).all()
    
    form.profesor_id.choices = [(0, 'Seleccionar profesor...')] + [(p.id, f"{p.nombres} {p.apellidos}") for p in profesores]
    form.curso_id.choices = [(0, 'Seleccionar curso...')] + [(c.id, f"{c.grado}{c.seccion}") for c in cursos]
    
    if form.validate_on_submit():
        # Validar que profesor y curso estén seleccionados
        if form.profesor_id.data == 0:
            flash('Debe seleccionar un profesor válido.', 'error')
            return render_template('admin/asignatura_form.html', form=form, asignatura=asignatura, title="Editar Asignatura")
        
        if form.curso_id.data == 0:
            flash('Debe seleccionar un curso válido.', 'error')
            return render_template('admin/asignatura_form.html', form=form, asignatura=asignatura, title="Editar Asignatura")
        
        asignatura.nombre = form.nombre.data
        asignatura.descripcion = form.descripcion.data
        asignatura.profesor_id = form.profesor_id.data
        asignatura.curso_id = form.curso_id.data
        asignatura.activa = form.activa.data
        
        db.session.commit()
        flash(f'Asignatura {asignatura.nombre} actualizada exitosamente.', 'success')
        return redirect(url_for('admin.asignaturas'))
    
    return render_template('admin/asignatura_form.html', form=form, asignatura=asignatura, title="Editar Asignatura")

@admin_bp.route('/asignaturas/<int:id>/eliminar', methods=['POST'])
@login_required
@admin_required
def eliminar_asignatura(id):
    """Eliminar una asignatura"""
    asignatura = db.session.get(Asignatura, id)
    if not asignatura:
        abort(404)
    
    nombre = asignatura.nombre
    db.session.delete(asignatura)
    db.session.commit()
    
    flash(f'Asignatura {nombre} eliminada exitosamente.', 'success')
    return redirect(url_for('admin.asignaturas'))

# === MÓDULO DE HORARIOS EN TIEMPO REAL ===

@admin_bp.route('/horarios')
@login_required
@admin_required
def horarios():
    """Panel de gestión de horarios y ausencias"""
    # Estadísticas del día
    hoy = datetime.now().date()
    ausencias_hoy = NotificacionReemplazo.query.filter(
        NotificacionReemplazo.fecha_ausencia >= hoy
    ).all()
    
    profesores_disponibles = Usuario.query.filter(
        Usuario.role == 'profesor',
        Usuario.activo == True
    ).all()
    
    # Horarios del día actual
    horarios_hoy = Horario.query.filter_by(
        dia_semana=hoy.strftime('%A'),
        activo=True
    ).order_by(Horario.hora_inicio).all()
    
    return render_template('admin/horarios.html',
                         ausencias_hoy=ausencias_hoy,
                         profesores_disponibles=profesores_disponibles,
                         horarios_hoy=horarios_hoy)

@admin_bp.route('/reportar-ausencia', methods=['GET', 'POST'])
@login_required
@admin_required
def reportar_ausencia():
    """Reportar ausencia de profesor"""
    form = AusenciaProfesorForm()
    
    # Cargar profesores
    profesores = Usuario.query.filter_by(role='profesor').order_by(Usuario.apellidos, Usuario.nombres).all()
    form.profesor_id.choices = [(p.id, f"{p.nombres} {p.apellidos}") for p in profesores]
    
    if form.validate_on_submit():
        # Buscar horarios afectados
        dia_semana = form.fecha_ausencia.data.strftime('%A')
        horarios_afectados = Horario.query.filter_by(
            profesor_id=form.profesor_id.data,
            dia_semana=dia_semana,
            activo=True
        ).all()
        
        for horario in horarios_afectados:
            # Buscar profesor de reemplazo
            profesor_reemplazo = buscar_profesor_reemplazo(horario)
            
            # Crear notificación
            notificacion = NotificacionReemplazo(
                profesor_ausente_id=form.profesor_id.data,
                profesor_reemplazo_id=profesor_reemplazo.id if profesor_reemplazo else None,
                horario_id=horario.id,
                fecha_ausencia=form.fecha_ausencia.data,
                motivo_ausencia=form.motivo.data,
                estado='pendiente' if profesor_reemplazo else 'sin_reemplazo'
            )
            
            db.session.add(notificacion)
        
        db.session.commit()
        
        total_horarios = len(horarios_afectados)
        reemplazos_encontrados = sum(1 for h in horarios_afectados if buscar_profesor_reemplazo(h))
        
        flash(f'Ausencia reportada. {reemplazos_encontrados} de {total_horarios} clases tienen reemplazo asignado.', 'info')
        return redirect(url_for('admin.horarios'))
    
    return render_template('admin/reportar_ausencia.html', form=form)

def buscar_profesor_reemplazo(horario):
    """
    Algoritmo para buscar profesor de reemplazo
    """
    # 1. Buscar profesores disponibles para reemplazo
    profesores_disponibles = Usuario.query.filter(
        Usuario.role == 'profesor',
        Usuario.activo == True,
        Usuario.id != horario.profesor_id
    ).all()
    
    if not profesores_disponibles:
        return None
    
    # 2. Filtrar por disponibilidad de horario
    profesores_libres = []
    for profesor in profesores_disponibles:
        # Verificar si el profesor tiene clases a esa hora
        conflicto = Horario.query.filter_by(
            profesor_id=profesor.id,
            dia_semana=horario.dia_semana,
            hora_inicio=horario.hora_inicio,
            activo=True
        ).first()
        
        if not conflicto:
            profesores_libres.append(profesor)
    
    if not profesores_libres:
        return None
    
    # 3. Priorizar por especialidad
    if horario.asignatura and horario.asignatura.nombre:
        for profesor in profesores_libres:
            if profesor.materia_especialidad and horario.asignatura.nombre.lower() in profesor.materia_especialidad.lower():
                return profesor
    
    # 4. Retornar el primero disponible
    return profesores_libres[0]

@admin_bp.route('/api/profesores-por-materia')
@login_required
@admin_required
def api_profesores_por_materia():
    """API para obtener profesores filtrados por materia"""
    materia = request.args.get('materia', '').strip()
    
    if not materia:
        profesores = Usuario.query.filter_by(role='profesor').order_by(Usuario.apellidos, Usuario.nombres).all()
    else:
        profesores = Usuario.query.filter(
            Usuario.role == 'profesor',
            Usuario.materia_especialidad.ilike(f'%{materia}%')
        ).order_by(Usuario.apellidos, Usuario.nombres).all()
    
    resultado = []
    for profesor in profesores:
        resultado.append({
            'id': profesor.id,
            'nombre_completo': f"{profesor.nombres} {profesor.apellidos}",
            'materia_especialidad': profesor.materia_especialidad or 'No especificada',
            'disponible_reemplazo': profesor.activo
        })
    
    return jsonify(resultado)

@admin_bp.route('/ausencias/<int:id>/confirmar', methods=['POST'])
@login_required
@admin_required
def confirmar_reemplazo(id):
    """Confirmar un reemplazo de profesor"""
    notificacion = db.session.get(NotificacionReemplazo, id)
    if not notificacion:
        abort(404)
    
    notificacion.estado = 'confirmado'
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Reemplazo confirmado'})

@admin_bp.route('/ausencias/<int:id>/rechazar', methods=['POST'])
@login_required
@admin_required
def rechazar_reemplazo(id):
    """Rechazar un reemplazo y buscar alternativa"""
    notificacion = db.session.get(NotificacionReemplazo, id)
    if not notificacion:
        abort(404)
    
    # Buscar nuevo profesor de reemplazo
    if notificacion.horario:
        nuevo_reemplazo = buscar_profesor_reemplazo(notificacion.horario)
        if nuevo_reemplazo:
            notificacion.profesor_reemplazo_id = nuevo_reemplazo.id
            notificacion.estado = 'pendiente'
        else:
            notificacion.profesor_reemplazo_id = None
            notificacion.estado = 'sin_reemplazo'
    
    db.session.commit()
    
    return jsonify({
        'success': True, 
        'message': 'Reemplazo actualizado',
        'nuevo_reemplazo': nuevo_reemplazo.nombres + ' ' + nuevo_reemplazo.apellidos if nuevo_reemplazo else None
    })


@admin_bp.route('/reportes')
@login_required
@admin_required
def reportes():
    """Panel de reportes y estadísticas"""
    from sqlalchemy import func
    
    # Estadísticas generales
    total_usuarios = Usuario.query.filter_by(activo=True).count()
    total_estudiantes = Usuario.query.filter_by(role='estudiante', activo=True).count()
    total_profesores = Usuario.query.filter_by(role='profesor', activo=True).count()
    total_cursos = Curso.query.filter_by(activo=True).count()
    total_asignaturas = Asignatura.query.filter_by(activa=True).count()
    total_calificaciones = Calificacion.query.count()
    
    # Estadísticas por curso usando la relación many-to-many
    estadisticas_cursos = []
    for curso in Curso.query.filter_by(activo=True).all():
        estudiantes_curso = Usuario.query.filter_by(role='estudiante', activo=True).filter(
            Usuario.cursos.contains(curso)
        ).all()
        
        # Calcular promedio de calificaciones para este curso
        calificaciones_curso = db.session.query(func.avg(Calificacion.nota)).join(
            Usuario, Calificacion.estudiante_id == Usuario.id
        ).filter(
            Usuario.cursos.contains(curso)
        ).scalar()
        
        estadisticas_cursos.append({
            'grado': curso.grado,
            'seccion': curso.seccion,
            'total_estudiantes': len(estudiantes_curso),
            'promedio_general': round(calificaciones_curso or 0, 2)
        })
    
    # Rendimiento por asignatura
    rendimiento_asignaturas = db.session.query(
        Asignatura.nombre,
        func.count(Calificacion.id).label('total_calificaciones'),
        func.avg(Calificacion.nota).label('promedio'),
        func.min(Calificacion.nota).label('nota_minima'),
        func.max(Calificacion.nota).label('nota_maxima')
    ).join(Tarea, Tarea.asignatura_id == Asignatura.id).join(
        Calificacion, Calificacion.tarea_id == Tarea.id
    ).filter(
        Asignatura.activa == True
    ).group_by(Asignatura.id, Asignatura.nombre).all()
    
    # Actividad reciente (últimas 10 calificaciones)
    actividad_reciente = db.session.query(Calificacion, Usuario, Tarea, Asignatura).join(
        Usuario, Calificacion.estudiante_id == Usuario.id
    ).join(
        Tarea, Calificacion.tarea_id == Tarea.id
    ).join(
        Asignatura, Tarea.asignatura_id == Asignatura.id
    ).order_by(Calificacion.fecha_calificacion.desc()).limit(10).all()
    
    return render_template('admin/reportes.html',
                         total_usuarios=total_usuarios,
                         total_estudiantes=total_estudiantes,
                         total_profesores=total_profesores,
                         total_cursos=total_cursos,
                         total_asignaturas=total_asignaturas,
                         total_calificaciones=total_calificaciones,
                         estadisticas_cursos=estadisticas_cursos,
                         rendimiento_asignaturas=rendimiento_asignaturas,
                         actividad_reciente=actividad_reciente)


@admin_bp.route('/configuracion')
@login_required
@admin_required
def configuracion():
    """Panel de configuración del sistema"""
    import os
    from datetime import datetime
    
    # Información del sistema
    db_path = os.path.join(current_app.instance_path, 'database.db')
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    db_size_mb = round(db_size / (1024 * 1024), 2)
    
    # Información de la aplicación
    app_info = {
        'version': '1.0.0',
        'ultimo_backup': None,  # Se puede implementar
        'uptime': datetime.now(),
        'bd_tamaño': db_size_mb
    }
    
    return render_template('admin/configuracion.html', app_info=app_info)


@admin_bp.route('/configuracion/backup')
@login_required
@admin_required
def crear_backup():
    """Crear backup de la base de datos"""
    import shutil
    from datetime import datetime
    
    try:
        # Crear nombre del backup con timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_colegio_{timestamp}.db'
        
        # Rutas
        db_path = os.path.join(current_app.instance_path, 'database.db')
        backup_path = os.path.join(current_app.instance_path, backup_filename)
        
        # Copiar base de datos
        shutil.copy2(db_path, backup_path)
        
        flash(f'Backup creado exitosamente: {backup_filename}', 'success')
        return send_file(backup_path, as_attachment=True, download_name=backup_filename)
        
    except Exception as e:
        flash(f'Error al crear backup: {str(e)}', 'error')
        return redirect(url_for('admin.configuracion'))


@admin_bp.route('/reportes/exportar')
@login_required
@admin_required
def exportar_reportes():
    """Exportar reportes en formato CSV"""
    import csv
    from io import StringIO
    
    # Crear CSV en memoria
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow(['Tipo', 'Descripción', 'Valor', 'Fecha'])
    
    # Datos básicos
    total_usuarios = Usuario.query.filter_by(activo=True).count()
    total_estudiantes = Usuario.query.filter_by(role='estudiante', activo=True).count()
    total_profesores = Usuario.query.filter_by(role='profesor', activo=True).count()
    
    writer.writerow(['Estadística', 'Total Usuarios', total_usuarios, datetime.now().strftime('%Y-%m-%d')])
    writer.writerow(['Estadística', 'Total Estudiantes', total_estudiantes, datetime.now().strftime('%Y-%m-%d')])
    writer.writerow(['Estadística', 'Total Profesores', total_profesores, datetime.now().strftime('%Y-%m-%d')])
    
    # Preparar respuesta
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=reporte_colegio_{datetime.now().strftime("%Y%m%d")}.csv'}
    )


@admin_bp.route('/estudiantes/buscar')
@login_required
@admin_required
def buscar_estudiantes():
    """Página para buscar y listar estudiantes"""
    from sqlalchemy import func
    
    # Obtener parámetros de búsqueda
    busqueda = request.args.get('busqueda', '').strip()
    curso_id = request.args.get('curso_id', type=int)
    
    # Consulta base de estudiantes
    query = Usuario.query.filter_by(role='estudiante', activo=True)
    
    # Aplicar filtros de búsqueda
    if busqueda:
        query = query.filter(
            db.or_(
                Usuario.nombres.ilike(f'%{busqueda}%'),
                Usuario.apellidos.ilike(f'%{busqueda}%'),
                Usuario.numero_documento.ilike(f'%{busqueda}%'),
                Usuario.email.ilike(f'%{busqueda}%')
            )
        )
    
    if curso_id:
        curso = Curso.query.get(curso_id)
        if curso:
            query = query.filter(Usuario.cursos.contains(curso))
    
    # Obtener estudiantes con estadísticas
    estudiantes = query.all()
    
    # Calcular estadísticas básicas para cada estudiante
    estudiantes_stats = []
    for estudiante in estudiantes:
        # Promedio general del estudiante
        promedio = db.session.query(func.avg(Calificacion.nota)).filter_by(
            estudiante_id=estudiante.id
        ).scalar() or 0
        
        # Total de calificaciones
        total_calificaciones = Calificacion.query.filter_by(estudiante_id=estudiante.id).count()
        
        # Cursos del estudiante
        cursos_estudiante = [f"{curso.grado}{curso.seccion}" for curso in estudiante.cursos]
        
        estudiantes_stats.append({
            'estudiante': estudiante,
            'promedio': round(promedio, 2),
            'total_calificaciones': total_calificaciones,
            'cursos': ', '.join(cursos_estudiante) if cursos_estudiante else 'Sin curso asignado'
        })
    
    # Obtener todos los cursos para el filtro
    cursos = Curso.query.filter_by(activo=True).order_by(Curso.grado, Curso.seccion).all()
    
    return render_template('admin/buscar_estudiantes.html',
                         estudiantes_stats=estudiantes_stats,
                         cursos=cursos,
                         busqueda=busqueda,
                         curso_id=curso_id)


@admin_bp.route('/estudiantes/<int:estudiante_id>/perfil')
@login_required
@admin_required
def perfil_estudiante(estudiante_id):
    """Perfil académico completo del estudiante"""
    from sqlalchemy import func
    
    # Obtener el estudiante
    estudiante = Usuario.query.filter_by(id=estudiante_id, role='estudiante').first()
    if not estudiante:
        flash('Estudiante no encontrado.', 'error')
        return redirect(url_for('admin.buscar_estudiantes'))
    
    # Información básica del estudiante
    cursos_estudiante = estudiante.cursos
    
    # Estadísticas generales
    total_calificaciones = Calificacion.query.filter_by(estudiante_id=estudiante.id).count()
    promedio_general = db.session.query(func.avg(Calificacion.nota)).filter_by(
        estudiante_id=estudiante.id
    ).scalar() or 0
    
    # Calificaciones por asignatura
    calificaciones_asignatura = db.session.query(
        Asignatura.nombre,
        func.count(Calificacion.id).label('total_notas'),
        func.avg(Calificacion.nota).label('promedio'),
        func.min(Calificacion.nota).label('nota_minima'),
        func.max(Calificacion.nota).label('nota_maxima')
    ).join(Tarea, Tarea.asignatura_id == Asignatura.id).join(
        Calificacion, Calificacion.tarea_id == Tarea.id
    ).filter(
        Calificacion.estudiante_id == estudiante.id
    ).group_by(Asignatura.id, Asignatura.nombre).all()
    
    # Últimas 10 calificaciones
    ultimas_calificaciones = db.session.query(Calificacion, Tarea, Asignatura).join(
        Tarea, Calificacion.tarea_id == Tarea.id
    ).join(
        Asignatura, Tarea.asignatura_id == Asignatura.id
    ).filter(
        Calificacion.estudiante_id == estudiante.id
    ).order_by(Calificacion.fecha_calificacion.desc()).limit(10).all()
    
    # Tareas pendientes/sin calificar
    from datetime import date, timedelta
    hoy = datetime.now()
    
    tareas_estudiante = db.session.query(Tarea, Asignatura).join(
        Asignatura, Tarea.asignatura_id == Asignatura.id
    ).filter(
        Tarea.fecha_entrega >= hoy,  # Solo tareas vigentes
        ~Tarea.id.in_(
            db.session.query(Calificacion.tarea_id).filter_by(estudiante_id=estudiante.id)
        )
    ).all()
    
    # Progreso académico por mes (últimos 6 meses)
    try:
        hace_seis_meses = hoy.replace(month=hoy.month-6) if hoy.month > 6 else hoy.replace(year=hoy.year-1, month=hoy.month+6)
    except ValueError:
        # Manejar el caso de fechas inválidas (como 31 de enero -> 31 de julio que no existe)
        hace_seis_meses = hoy - timedelta(days=180)
    
    progreso_mensual = db.session.query(
        func.strftime('%Y-%m', Calificacion.fecha_calificacion).label('mes'),
        func.avg(Calificacion.nota).label('promedio_mes'),
        func.count(Calificacion.id).label('total_calificaciones')
    ).filter(
        Calificacion.estudiante_id == estudiante.id,
        Calificacion.fecha_calificacion >= hace_seis_meses
    ).group_by(func.strftime('%Y-%m', Calificacion.fecha_calificacion)).order_by('mes').all()
    
    return render_template('admin/perfil_estudiante.html',
                         estudiante=estudiante,
                         cursos_estudiante=cursos_estudiante,
                         total_calificaciones=total_calificaciones,
                         promedio_general=round(promedio_general, 2),
                         calificaciones_asignatura=calificaciones_asignatura,
                         ultimas_calificaciones=ultimas_calificaciones,
                         tareas_pendientes=tareas_estudiante,
                         progreso_mensual=progreso_mensual)