#!/usr/bin/env python3
"""
Script para generar calificaciones de los 3 primeros períodos académicos
para todos los estudiantes del Colegio Colombia
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Usuario, Curso, Asignatura, Calificacion, Tarea
from app import create_app
from datetime import datetime, date
import random

def generar_calificaciones_periodo():
    """Generar calificaciones realistas para los 3 primeros períodos"""
    
    app = create_app()
    
    with app.app_context():
        print("📊 GENERANDO CALIFICACIONES - COLEGIO COLOMBIA")
        print("=" * 60)
        
        # Limpiar calificaciones existentes
        print("1. Limpiando calificaciones anteriores...")
        Calificacion.query.delete()
        db.session.commit()
        print("   ✅ Calificaciones anteriores eliminadas")
        
        # Obtener estudiantes y asignaturas
        estudiantes = Usuario.query.filter_by(role='estudiante').all()
        asignaturas = Asignatura.query.all()
        
        if not estudiantes:
            print("❌ No hay estudiantes en la base de datos")
            return False
            
        if not asignaturas:
            print("❌ No hay asignaturas en la base de datos")
            return False
        
        print(f"📚 Estudiantes encontrados: {len(estudiantes)}")
        print(f"📋 Asignaturas encontradas: {len(asignaturas)}")
        
        # Períodos académicos
        periodos = [
            {"numero": 1, "nombre": "Primer Período", "fecha_inicio": date(2025, 1, 15), "fecha_fin": date(2025, 3, 30)},
            {"numero": 2, "nombre": "Segundo Período", "fecha_inicio": date(2025, 4, 1), "fecha_fin": date(2025, 6, 15)},
            {"numero": 3, "nombre": "Tercer Período", "fecha_inicio": date(2025, 7, 15), "fecha_fin": date(2025, 9, 30)}
        ]
        
        print(f"\n📅 Generando calificaciones para {len(periodos)} períodos:")
        for periodo in periodos:
            print(f"   📖 {periodo['nombre']}: {periodo['fecha_inicio']} - {periodo['fecha_fin']}")
        
        calificaciones_creadas = 0
        
        for periodo in periodos:
            print(f"\n🔄 Procesando {periodo['nombre']}...")
            
            for estudiante in estudiantes:
                # Obtener asignaturas del curso del estudiante
                asignaturas_estudiante = []
                
                if estudiante.cursos:
                    curso_estudiante = estudiante.cursos[0]  # Primer curso asignado
                    asignaturas_estudiante = Asignatura.query.filter_by(curso_id=curso_estudiante.id).all()
                
                if not asignaturas_estudiante:
                    # Si no hay asignaturas específicas, usar algunas generales
                    asignaturas_estudiante = asignaturas[:6]  # Primeras 6 asignaturas
                
                # Generar calificaciones para cada asignatura
                for asignatura in asignaturas_estudiante:
                    # Generar nota realista basada en el rendimiento del estudiante
                    nota = generar_nota_realista(estudiante, asignatura, periodo['numero'])
                    
                    # Crear una tarea ficticia para el período si no existe
                    tarea_periodo = Tarea.query.filter_by(
                        asignatura_id=asignatura.id,
                        titulo=f"Evaluación {periodo['nombre']}"
                    ).first()
                    
                    if not tarea_periodo:
                        # Crear tarea de evaluación para el período
                        tarea_periodo = Tarea(
                            titulo=f"Evaluación {periodo['nombre']}",
                            descripcion=f"Evaluación general del {periodo['nombre']} para {asignatura.nombre}",
                            asignatura_id=asignatura.id,
                            profesor_id=asignatura.profesor_id,
                            fecha_entrega=periodo['fecha_fin'],
                            activa=True
                        )
                        db.session.add(tarea_periodo)
                        db.session.flush()  # Para obtener el ID
                    
                    calificacion = Calificacion(
                        estudiante_id=estudiante.id,
                        tarea_id=tarea_periodo.id,
                        nota=nota,
                        comentarios=generar_observacion(nota, asignatura.nombre),
                        fecha_calificacion=periodo['fecha_fin'],
                        periodo=str(periodo['numero'])
                    )
                    
                    db.session.add(calificacion)
                    calificaciones_creadas += 1
            
            # Guardar por período para evitar problemas de memoria
            db.session.commit()
            print(f"   ✅ {periodo['nombre']} completado")
        
        print(f"\n✅ CALIFICACIONES GENERADAS EXITOSAMENTE")
        print(f"📊 Total calificaciones creadas: {calificaciones_creadas}")
        
        # Mostrar estadísticas por período
        print(f"\n📈 ESTADÍSTICAS POR PERÍODO:")
        for periodo in periodos:
            califs_periodo = Calificacion.query.filter_by(periodo=str(periodo['numero'])).count()
            promedio_periodo = db.session.query(db.func.avg(Calificacion.nota)).filter_by(periodo=str(periodo['numero'])).scalar()
            
            print(f"   📖 {periodo['nombre']}:")
            print(f"      📊 Calificaciones: {califs_periodo}")
            print(f"      📈 Promedio general: {promedio_periodo:.2f}" if promedio_periodo else "      📈 Promedio: N/A")
        
        # Mostrar ejemplos de calificaciones
        print(f"\n📋 EJEMPLOS DE CALIFICACIONES:")
        ejemplos = Calificacion.query.limit(10).all()
        for cal in ejemplos:
            estudiante = Usuario.query.get(cal.estudiante_id)
            tarea = Tarea.query.get(cal.tarea_id)
            asignatura = Asignatura.query.get(tarea.asignatura_id) if tarea else None
            asignatura_nombre = asignatura.nombre if asignatura else "Materia desconocida"
            print(f"   📚 {estudiante.nombres} {estudiante.apellidos} - {asignatura_nombre} P{cal.periodo}: {cal.nota}")
        
        return True

def generar_nota_realista(estudiante, asignatura, periodo):
    """Generar una nota realista entre 0.0 y 5.0"""
    
    # Factores que influyen en la nota
    rendimiento_base = random.uniform(2.5, 4.5)  # Rendimiento base del estudiante
    
    # Ajustes por materia (algunas materias son más difíciles)
    dificultad_materia = {
        'Matemáticas': -0.3,
        'Física': -0.2,
        'Química': -0.2,
        'Inglés': -0.1,
        'Español': 0.1,
        'Ciencias Sociales': 0.1,
        'Historia': 0.1,
        'Educación Física': 0.3,
        'Artes': 0.2,
        'Música': 0.2,
        'Informática': 0.0,
        'Tecnología': 0.0
    }
    
    ajuste_materia = dificultad_materia.get(asignatura.nombre, 0.0)
    
    # Progresión a lo largo del año (los estudiantes mejoran)
    progresion_periodo = {
        1: -0.1,  # Primer período: adaptación
        2: 0.0,   # Segundo período: estabilidad
        3: 0.1    # Tercer período: mejora
    }
    
    ajuste_periodo = progresion_periodo.get(periodo, 0.0)
    
    # Calcular nota final
    nota_final = rendimiento_base + ajuste_materia + ajuste_periodo
    
    # Agregar algo de variabilidad
    nota_final += random.uniform(-0.3, 0.3)
    
    # Asegurar que esté en el rango válido (0.0 - 5.0)
    nota_final = max(0.0, min(5.0, nota_final))
    
    # Redondear a un decimal
    return round(nota_final, 1)

def generar_observacion(nota, materia):
    """Generar observación basada en la nota"""
    
    if nota >= 4.5:
        observaciones_excelente = [
            "Excelente desempeño, demuestra dominio completo de la materia",
            "Sobresaliente, supera las expectativas del período",
            "Desempeño excepcional, ejemplo para sus compañeros",
            "Excelente participación y comprensión de los temas"
        ]
        return random.choice(observaciones_excelente)
    
    elif nota >= 4.0:
        observaciones_buenas = [
            "Buen desempeño, cumple con los objetivos propuestos",
            "Desempeño satisfactorio, demuestra comprensión de los temas",
            "Buen nivel académico, se esfuerza por mejorar",
            "Desempeño apropiado para el nivel académico"
        ]
        return random.choice(observaciones_buenas)
    
    elif nota >= 3.0:
        observaciones_aceptables = [
            "Desempeño básico, necesita reforzar algunos conceptos",
            "Cumple con los mínimos requeridos, puede mejorar",
            "Nivel aceptable, se recomienda mayor dedicación",
            "Progreso adecuado, debe seguir esforzándose"
        ]
        return random.choice(observaciones_aceptables)
    
    else:
        observaciones_deficientes = [
            "Bajo desempeño, requiere refuerzo académico urgente",
            "No alcanza los objetivos mínimos, necesita apoyo",
            "Desempeño deficiente, debe mejorar significativamente",
            "Requiere atención especial y refuerzo en la materia"
        ]
        return random.choice(observaciones_deficientes)

def mostrar_reporte_completo():
    """Mostrar reporte completo de calificaciones"""
    
    app = create_app()
    
    with app.app_context():
        print(f"\n📊 REPORTE COMPLETO DE CALIFICACIONES")
        print("=" * 60)
        
        # Estadísticas generales
        total_calificaciones = Calificacion.query.count()
        total_estudiantes = Usuario.query.filter_by(role='estudiante').count()
        promedio_general = db.session.query(db.func.avg(Calificacion.nota)).scalar()
        
        print(f"📈 ESTADÍSTICAS GENERALES:")
        print(f"   👥 Total estudiantes: {total_estudiantes}")
        print(f"   📊 Total calificaciones: {total_calificaciones}")
        print(f"   📈 Promedio general: {promedio_general:.2f}" if promedio_general else "   📈 Promedio: N/A")
        
        # Top 5 estudiantes
        print(f"\n🏆 TOP 5 ESTUDIANTES (PROMEDIO GENERAL):")
        top_estudiantes = db.session.query(
            Usuario.nombres, 
            Usuario.apellidos,
            db.func.avg(Calificacion.nota).label('promedio')
        ).join(Calificacion).filter(Usuario.role == 'estudiante').group_by(Usuario.id).order_by(db.func.avg(Calificacion.nota).desc()).limit(5).all()
        
        for i, (nombres, apellidos, promedio) in enumerate(top_estudiantes, 1):
            print(f"   {i}. {nombres} {apellidos}: {promedio:.2f}")
        
        # Estadísticas por materia
        print(f"\n📚 PROMEDIO POR MATERIA:")
        promedios_materia = db.session.query(
            Asignatura.nombre,
            db.func.avg(Calificacion.nota).label('promedio'),
            db.func.count(Calificacion.id).label('total_notas')
        ).join(Tarea).join(Calificacion).group_by(Asignatura.nombre).order_by(db.func.avg(Calificacion.nota).desc()).all()
        
        for materia, promedio, total in promedios_materia:
            print(f"   📖 {materia}: {promedio:.2f} ({total} calificaciones)")

if __name__ == "__main__":
    print("📊 GENERADOR DE CALIFICACIONES - COLEGIO COLOMBIA")
    print("=" * 70)
    
    try:
        if generar_calificaciones_periodo():
            mostrar_reporte_completo()
            
            print(f"\n🎯 PROCESO COMPLETADO EXITOSAMENTE")
            print(f"✅ Calificaciones de 3 períodos generadas para todos los estudiantes")
            print(f"📊 Sistema de calificación: 0.0 - 5.0 (estilo colombiano)")
            print(f"📈 Distribución realista con variabilidad por materia y período")
            
        else:
            print("❌ Error en la generación de calificaciones")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)