from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from models import Horario, Usuario, Curso, Asignatura, NotificacionReemplazo
from extensions import db
from datetime import datetime, date

horario_bp = Blueprint('horario', __name__)

@horario_bp.route('/tiempo_real')
@login_required
def tiempo_real():
    """Vista del sistema de horarios en tiempo real"""
    if not (current_user.es_admin or current_user.es_profesor):
        return redirect(url_for('main.index'))
    
    fecha_actual = date.today()
    dia_semana = fecha_actual.weekday()
    
    if dia_semana > 4:  # Fin de semana
        return render_template('horario/tiempo_real.html', 
                             mensaje="No hay clases programadas para fines de semana",
                             fecha_actual=fecha_actual)
    
    # Obtener horarios del día actual
    horarios_dia = Horario.query.filter_by(
        dia_semana=dia_semana,
        activo=True
    ).order_by(Horario.hora_inicio).all()
    
    # Obtener notificaciones de reemplazo para hoy
    notificaciones_hoy = NotificacionReemplazo.query.filter_by(
        fecha_ausencia=fecha_actual
    ).all()
    
    # Identificar clases afectadas por ausencias
    clases_afectadas = []
    for notif in notificaciones_hoy:
        if notif.horario_original in horarios_dia:
            clases_afectadas.append({
                'horario': notif.horario_original,
                'notificacion': notif,
                'estado_reemplazo': notif.estado
            })
    
    return render_template('horario/tiempo_real.html',
                         horarios_dia=horarios_dia,
                         clases_afectadas=clases_afectadas,
                         fecha_actual=fecha_actual,
                         dia_nombre=['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][dia_semana])

@horario_bp.route('/api/estado_actual')
@login_required
def api_estado_actual():
    """API para obtener el estado actual de horarios (para actualizaciones en tiempo real)"""
    fecha_actual = date.today()
    dia_semana = fecha_actual.weekday()
    
    if dia_semana > 4:
        return jsonify({'error': 'No hay clases en fines de semana'})
    
    hora_actual = datetime.now().time()
    
    # Buscar la clase actual
    clase_actual = Horario.query.filter(
        Horario.dia_semana == dia_semana,
        Horario.hora_inicio <= hora_actual,
        Horario.hora_fin >= hora_actual,
        Horario.activo == True
    ).first()
    
    # Buscar la próxima clase
    proxima_clase = Horario.query.filter(
        Horario.dia_semana == dia_semana,
        Horario.hora_inicio > hora_actual,
        Horario.activo == True
    ).order_by(Horario.hora_inicio).first()
    
    # Verificar cambios por reemplazos
    cambios_hoy = NotificacionReemplazo.query.filter_by(
        fecha_ausencia=fecha_actual,
        estado='confirmado'
    ).all()
    
    resultado = {
        'fecha': fecha_actual.isoformat(),
        'hora_actual': hora_actual.strftime('%H:%M'),
        'dia_semana': ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][dia_semana],
        'clase_actual': None,
        'proxima_clase': None,
        'cambios_confirmados': len(cambios_hoy)
    }
    
    if clase_actual:
        resultado['clase_actual'] = {
            'asignatura': clase_actual.asignatura.nombre,
            'profesor': clase_actual.profesor.nombre_completo,
            'curso': clase_actual.curso.nombre_completo,
            'aula': clase_actual.aula,
            'hora_inicio': clase_actual.hora_inicio.strftime('%H:%M'),
            'hora_fin': clase_actual.hora_fin.strftime('%H:%M')
        }
        
        # Verificar si hay reemplazo para esta clase
        reemplazo = NotificacionReemplazo.query.filter_by(
            horario_id=clase_actual.id,
            fecha_ausencia=fecha_actual,
            estado='confirmado'
        ).first()
        
        if reemplazo:
            resultado['clase_actual']['profesor_reemplazo'] = reemplazo.profesor_reemplazo.nombre_completo
            resultado['clase_actual']['tiene_reemplazo'] = True
    
    if proxima_clase:
        resultado['proxima_clase'] = {
            'asignatura': proxima_clase.asignatura.nombre,
            'profesor': proxima_clase.profesor.nombre_completo,
            'curso': proxima_clase.curso.nombre_completo,
            'aula': proxima_clase.aula,
            'hora_inicio': proxima_clase.hora_inicio.strftime('%H:%M'),
            'hora_fin': proxima_clase.hora_fin.strftime('%H:%M')
        }
    
    return jsonify(resultado)

@horario_bp.route('/api/notificaciones_estudiantes/<int:curso_id>')
@login_required
def api_notificaciones_estudiantes(curso_id):
    """API para obtener las notificaciones que deben enviarse a los estudiantes de un curso"""
    if not current_user.es_admin:
        return jsonify({'error': 'Acceso denegado'}), 403
    
    fecha_actual = date.today()
    
    # Buscar cambios confirmados para el curso
    cambios = db.session.query(NotificacionReemplazo).join(Horario).filter(
        Horario.curso_id == curso_id,
        NotificacionReemplazo.fecha_ausencia == fecha_actual,
        NotificacionReemplazo.estado == 'confirmado'
    ).all()
    
    notificaciones = []
    for cambio in cambios:
        notificaciones.append({
            'clase': {
                'asignatura': cambio.horario_original.asignatura.nombre,
                'hora_inicio': cambio.horario_original.hora_inicio.strftime('%H:%M'),
                'hora_fin': cambio.horario_original.hora_fin.strftime('%H:%M'),
                'aula': cambio.horario_original.aula
            },
            'profesor_ausente': cambio.profesor_ausente.nombre_completo,
            'profesor_reemplazo': cambio.profesor_reemplazo.nombre_completo,
            'mensaje': f"CAMBIO DE PROFESOR: La clase de {cambio.horario_original.asignatura.nombre} de {cambio.horario_original.hora_inicio.strftime('%H:%M')} a {cambio.horario_original.hora_fin.strftime('%H:%M')} será dictada por {cambio.profesor_reemplazo.nombre_completo} debido a la ausencia de {cambio.profesor_ausente.nombre_completo}."
        })
    
    return jsonify({
        'curso': db.session.get(Curso, curso_id).nombre_completo,
        'notificaciones': notificaciones,
        'total': len(notificaciones)
    })

@horario_bp.route('/resumen_semanal')
@login_required
def resumen_semanal():
    """Ver resumen semanal de horarios y cambios"""
    if not (current_user.es_admin or current_user.es_profesor):
        return redirect(url_for('main.index'))
    
    # Obtener horarios de toda la semana
    horarios_semana = {}
    for dia in range(5):  # Lunes a Viernes
        horarios_dia = Horario.query.filter_by(
            dia_semana=dia,
            activo=True
        ).order_by(Horario.hora_inicio).all()
        dia_nombre = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes'][dia]
        horarios_semana[dia_nombre] = horarios_dia
    
    return render_template('horario/resumen_semanal.html',
                         horarios_semana=horarios_semana)