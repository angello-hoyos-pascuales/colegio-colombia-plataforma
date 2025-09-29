#!/usr/bin/env python3
"""
Script para verificar y crear asignaturas necesarias antes de generar calificaciones
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import db, Usuario, Curso, Asignatura, Calificacion
from app import create_app
from datetime import datetime

def verificar_y_crear_asignaturas():
    """Verificar estructura de la base de datos y crear asignaturas si es necesario"""
    
    app = create_app()
    
    with app.app_context():
        print("🔍 VERIFICANDO ESTRUCTURA DE LA BASE DE DATOS")
        print("=" * 60)
        
        # Verificar estudiantes
        estudiantes = Usuario.query.filter_by(role='estudiante').all()
        print(f"👥 Estudiantes: {len(estudiantes)}")
        
        # Verificar cursos
        cursos = Curso.query.all()
        print(f"📚 Cursos: {len(cursos)}")
        
        # Verificar asignaturas
        asignaturas = Asignatura.query.all()
        print(f"📖 Asignaturas: {len(asignaturas)}")
        
        # Verificar profesores
        profesores = Usuario.query.filter_by(role='profesor').all()
        print(f"👨‍🏫 Profesores: {len(profesores)}")
        
        if not asignaturas and cursos:
            print("\n🔧 CREANDO ASIGNATURAS PARA TODOS LOS CURSOS...")
            
            # Materias estándar por grado
            materias_basicas = [
                "Matemáticas",
                "Español",
                "Inglés",
                "Ciencias Naturales",
                "Ciencias Sociales",
                "Educación Física",
                "Artes",
                "Tecnología e Informática"
            ]
            
            # Materias adicionales para grados superiores
            materias_superiores = {
                "9": ["Física", "Química"],
                "10": ["Física", "Química", "Filosofía"],
                "11": ["Física", "Química", "Filosofía", "Economía"]
            }
            
            asignaturas_creadas = 0
            
            for curso in cursos:
                print(f"\n📚 Creando asignaturas para {curso.nombre}...")
                
                # Asignaturas básicas
                for materia in materias_basicas:
                    # Buscar profesor disponible (de forma cíclica)
                    profesor = profesores[asignaturas_creadas % len(profesores)] if profesores else None
                    
                    asignatura = Asignatura(
                        nombre=materia,
                        descripcion=f"{materia} para {curso.nombre}",
                        curso_id=curso.id,
                        profesor_id=profesor.id if profesor else None,
                        activa=True
                    )
                    
                    db.session.add(asignatura)
                    asignaturas_creadas += 1
                    print(f"   ✅ {materia} - Profesor: {profesor.nombres if profesor else 'Sin asignar'}")
                
                # Asignaturas adicionales para grados superiores
                grado_str = str(curso.grado)
                if grado_str in materias_superiores:
                    for materia in materias_superiores[grado_str]:
                        profesor = profesores[asignaturas_creadas % len(profesores)] if profesores else None
                        
                        asignatura = Asignatura(
                            nombre=materia,
                            descripcion=f"{materia} para {curso.nombre}",
                            curso_id=curso.id,
                            profesor_id=profesor.id if profesor else None,
                            activa=True
                        )
                        
                        db.session.add(asignatura)
                        asignaturas_creadas += 1
                        print(f"   ✅ {materia} (Adicional) - Profesor: {profesor.nombres if profesor else 'Sin asignar'}")
            
            db.session.commit()
            print(f"\n✅ Se crearon {asignaturas_creadas} asignaturas exitosamente")
            
        else:
            print("\n✅ Las asignaturas ya existen en la base de datos")
        
        # Mostrar resumen final
        print(f"\n📊 RESUMEN FINAL:")
        estudiantes = Usuario.query.filter_by(role='estudiante').count()
        profesores = Usuario.query.filter_by(role='profesor').count()
        cursos = Curso.query.count()
        asignaturas = Asignatura.query.count()
        
        print(f"   👥 Estudiantes: {estudiantes}")
        print(f"   👨‍🏫 Profesores: {profesores}")
        print(f"   📚 Cursos: {cursos}")
        print(f"   📖 Asignaturas: {asignaturas}")
        
        return asignaturas > 0

if __name__ == "__main__":
    print("🔧 VERIFICADOR DE ESTRUCTURA - COLEGIO COLOMBIA")
    print("=" * 70)
    
    try:
        if verificar_y_crear_asignaturas():
            print(f"\n🎯 ESTRUCTURA VERIFICADA Y LISTA")
            print(f"✅ Base de datos preparada para generar calificaciones")
        else:
            print("❌ Error en la verificación de estructura")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)