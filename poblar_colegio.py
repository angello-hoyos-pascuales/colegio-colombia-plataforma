#!/usr/bin/env python3
"""
Script para poblar la base de datos del Colegio Colombia
con profesores, estudiantes, cursos, asignaturas y horarios
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, Usuario, Curso, Asignatura, Tarea, Horario, Calificacion
from datetime import datetime, date, time, timedelta
from werkzeug.security import generate_password_hash
import random

# Datos para generar estudiantes y profesores
NOMBRES_ESTUDIANTES = [
    'Alejandro', 'Andrea', 'Andrés', 'Ana', 'Antonio', 'Beatriz', 'Carlos', 'Camila', 'Christian',
    'Catalina', 'Daniel', 'Diana', 'Diego', 'Daniela', 'Eduardo', 'Elena', 'Fernando', 'Fernanda',
    'Gabriel', 'Gabriela', 'Gustavo', 'Gloria', 'Héctor', 'Helena', 'Iván', 'Isabel', 'Javier',
    'Jessica', 'Jorge', 'Julia', 'Kevin', 'Karen', 'Leonardo', 'Laura', 'Manuel', 'María',
    'Nicolás', 'Natalia', 'Oscar', 'Olivia', 'Pablo', 'Paola', 'Rafael', 'Raquel', 'Santiago',
    'Sara', 'Sebastián', 'Sofía', 'Tomás', 'Teresa', 'Valentín', 'Valeria', 'Víctor', 'Victoria'
]

APELLIDOS = [
    'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 'Pérez',
    'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández', 'Díaz', 'Moreno', 'Álvarez', 'Muñoz',
    'Romero', 'Alonso', 'Gutiérrez', 'Navarro', 'Torres', 'Domínguez', 'Vázquez', 'Ramos',
    'Gil', 'Ramírez', 'Serrano', 'Blanco', 'Suárez', 'Molina', 'Morales', 'Ortega', 'Delgado',
    'Castro', 'Ortiz', 'Rubio', 'Marín', 'Sanz', 'Iglesias', 'Medina', 'Garrido', 'Cortés'
]

NOMBRES_PROFESORES = [
    'Alberto', 'Adriana', 'Arturo', 'Alejandra', 'Bruno', 'Beatriz', 'César', 'Carmen',
    'David', 'Dolores', 'Emilio', 'Eva', 'Francisco', 'Francisca', 'Gonzalo', 'Graciela',
    'Ignacio', 'Inmaculada', 'José', 'Josefa', 'Luis', 'Lucía', 'Miguel', 'Mercedes',
    'Pedro', 'Pilar', 'Ricardo', 'Rosa', 'Sergio', 'Silvia', 'Vicente', 'Violeta'
]

# Materias por grado
MATERIAS_POR_GRADO = {
    '6º': ['Matemáticas', 'Español', 'Ciencias Naturales', 'Sociales', 'Inglés', 'Educación Física', 'Artística', 'Ética', 'Religión'],
    '7º': ['Matemáticas', 'Español', 'Ciencias Naturales', 'Sociales', 'Inglés', 'Educación Física', 'Artística', 'Ética', 'Religión'],
    '8º': ['Matemáticas', 'Español', 'Biología', 'Sociales', 'Inglés', 'Educación Física', 'Artística', 'Ética', 'Religión'],
    '9º': ['Matemáticas', 'Español', 'Biología', 'Química', 'Física', 'Sociales', 'Inglés', 'Educación Física', 'Filosofía'],
    '10º': ['Matemáticas', 'Español', 'Biología', 'Química', 'Física', 'Sociales', 'Inglés', 'Educación Física', 'Filosofía', 'Economía'],
    '11º': ['Matemáticas', 'Español', 'Biología', 'Química', 'Física', 'Sociales', 'Inglés', 'Educación Física', 'Filosofía', 'Economía']
}

def normalizar_texto(texto):
    """Normalizar texto eliminando tildes y caracteres especiales"""
    texto = texto.lower()
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'ñ': 'n', 'ü': 'u'
    }
    for original, reemplazo in reemplazos.items():
        texto = texto.replace(original, reemplazo)
    return texto

def reiniciar_base_datos():
    """Reiniciar la base de datos manteniendo solo el administrador"""
    app = create_app()
    
    with app.app_context():
        print("🔄 REINICIANDO BASE DE DATOS...")
        
        # Mantener admin
        admin = Usuario.query.filter_by(role='admin').first()
        
        # Eliminar relaciones primero
        db.session.execute(db.text("DELETE FROM usuario_curso"))
        
        # Eliminar registros
        Calificacion.query.delete()
        Horario.query.delete()
        Tarea.query.delete()
        Asignatura.query.delete()
        Usuario.query.filter(Usuario.role != 'admin').delete()
        Curso.query.delete()
        
        db.session.commit()
        print("   ✅ Base de datos limpia")
        
        return app

def crear_cursos(app):
    """Crear todos los cursos del colegio"""
    with app.app_context():
        print("\n📚 CREANDO CURSOS...")
        
        cursos_data = [
            ('6º', 'A'), ('6º', 'B'),
            ('7º', 'A'), ('7º', 'B'),
            ('8º', 'A'), ('8º', 'B'),
            ('9º', 'A'), ('9º', 'B'),
            ('10º', 'A'), ('10º', 'B'),
            ('11º', 'A'), ('11º', 'B')
        ]
        
        for grado, seccion in cursos_data:
            curso = Curso(
                grado=grado,
                seccion=seccion,
                año_academico=2025,
                activo=True
            )
            db.session.add(curso)
            print(f"   📖 Curso creado: {grado} {seccion}")
        
        db.session.commit()
        print("   ✅ Cursos creados exitosamente")

def crear_profesores(app):
    """Crear profesores especializados"""
    with app.app_context():
        print("\n👨‍🏫 CREANDO PROFESORES...")
        
        # Especializaciones de profesores
        especialidades = [
            'Matemáticas', 'Español', 'Ciencias Naturales', 'Biología', 'Química', 
            'Física', 'Sociales', 'Inglés', 'Educación Física', 'Artística', 
            'Ética', 'Religión', 'Filosofía', 'Economía'
        ]
        
        emails_usados = set()
        profesores_creados = 0
        
        for i in range(len(especialidades)):
            # Generar combinación única de nombre y apellido
            intentos = 0
            while intentos < 10:  # Máximo 10 intentos para evitar loop infinito
                nombre = random.choice(NOMBRES_PROFESORES)
                apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
                
                # Normalizar email sin caracteres especiales
                nombre_email = normalizar_texto(nombre)
                apellido_email = normalizar_texto(apellidos.split()[0])
                email = f"{nombre_email}.{apellido_email}@colegiocolombia.edu.co"
                
                if email not in emails_usados:
                    emails_usados.add(email)
                    break
                intentos += 1
            
            # Si no se pudo generar email único, añadir número
            if email in emails_usados:
                email = f"{nombre_email}.{apellido_email}{i}@colegiocolombia.edu.co"
            
            profesor = Usuario(
                nombres=nombre,
                apellidos=apellidos,
                email=email,
                password_hash=generate_password_hash('profesor123'),
                role='profesor',
                tipo_documento='C.C.',
                numero_documento=f"1234567{80 + i:02d}",
                telefono=f"300123456{i:02d}",
                activo=True,
                fecha_creacion=datetime.now()
            )
            
            db.session.add(profesor)
            profesores_creados += 1
            print(f"   👨‍🏫 Profesor creado: {nombre} {apellidos} - Especialidad: {especialidades[i]}")
        
        db.session.commit()
        print(f"   ✅ {profesores_creados} profesores creados")

def crear_estudiantes(app, num_estudiantes=50):
    """Crear estudiantes distribuidos en cursos"""
    with app.app_context():
        print(f"\n🎓 CREANDO {num_estudiantes} ESTUDIANTES...")
        
        cursos = Curso.query.all()
        estudiantes_por_curso = num_estudiantes // len(cursos)
        
        emails_usados = set()
        estudiante_num = 1
        
        for curso in cursos:
            print(f"   📚 Asignando estudiantes a {curso.nombre_completo}...")
            
            for i in range(estudiantes_por_curso):
                # Generar combinación única de nombre y apellido
                intentos = 0
                while intentos < 10:
                    nombre = random.choice(NOMBRES_ESTUDIANTES)
                    apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
                    
                    # Normalizar email sin caracteres especiales
                    nombre_email = normalizar_texto(nombre)
                    apellido_email = normalizar_texto(apellidos.split()[0])
                    email = f"{nombre_email}.{apellido_email}@estudiante.colegiocolombia.edu.co"
                    
                    if email not in emails_usados:
                        emails_usados.add(email)
                        break
                    intentos += 1
                
                # Si no se pudo generar email único, añadir número
                if email in emails_usados:
                    email = f"{nombre_email}.{apellido_email}{estudiante_num}@estudiante.colegiocolombia.edu.co"
                
                estudiante = Usuario(
                    nombres=nombre,
                    apellidos=apellidos,
                    email=email,
                    password_hash=generate_password_hash('estudiante123'),
                    role='estudiante',
                    tipo_documento='T.I.',
                    numero_documento=f"9876543{estudiante_num:02d}",
                    telefono=f"301987654{estudiante_num:02d}",
                    activo=True,
                    fecha_creacion=datetime.now()
                )
                
                db.session.add(estudiante)
                estudiante.cursos.append(curso)
                estudiante_num += 1
        
        db.session.commit()
        print(f"   ✅ {num_estudiantes} estudiantes creados y distribuidos")

def crear_asignaturas(app):
    """Crear asignaturas por curso con profesores asignados"""
    with app.app_context():
        print("\n📖 CREANDO ASIGNATURAS...")
        
        cursos = Curso.query.all()
        profesores = Usuario.query.filter_by(role='profesor').all()
        profesor_index = 0
        
        for curso in cursos:
            materias = MATERIAS_POR_GRADO.get(curso.grado, [])
            
            for materia in materias:
                profesor = profesores[profesor_index % len(profesores)]
                
                asignatura = Asignatura(
                    nombre=materia,
                    descripcion=f"{materia} para {curso.nombre}",
                    curso_id=curso.id,
                    profesor_id=profesor.id,
                    activa=True
                )
                
                db.session.add(asignatura)
                profesor_index += 1
                print(f"     📚 {materia} - Profesor: {profesor.nombres}")
        
        db.session.commit()
        print("   ✅ Asignaturas creadas con profesores asignados")

def crear_horarios(app):
    """Crear horarios de clases"""
    with app.app_context():
        print("\n🕐 CREANDO HORARIOS...")
        
        asignaturas = Asignatura.query.all()
        
        dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes']
        horas_inicio = [
            time(7, 0), time(8, 0), time(9, 15), time(10, 15), 
            time(11, 15), time(14, 0), time(15, 0), time(16, 0)
        ]
        
        horarios_creados = 0
        for asignatura in asignaturas:
            # Crear 2-3 horarios por asignatura
            for i in range(random.randint(2, 3)):
                dia = random.randint(0, 4)  # Lunes a Viernes
                hora = random.choice(horas_inicio)
                
                horario = Horario(
                    asignatura_id=asignatura.id,
                    curso_id=asignatura.curso_id,  # Obtener curso_id de la asignatura
                    profesor_id=asignatura.profesor_id,  # Obtener profesor_id de la asignatura
                    dia_semana=dia,
                    hora_inicio=hora,
                    hora_fin=time(hora.hour + 1, hora.minute),
                    aula=f"Aula {random.randint(101, 320)}",
                    activo=True
                )
                
                db.session.add(horario)
                horarios_creados += 1
        
        db.session.commit()
        print(f"   ✅ {horarios_creados} horarios creados")

def crear_tareas_muestra(app):
    """Crear algunas tareas de muestra"""
    with app.app_context():
        print("\n📝 CREANDO TAREAS DE MUESTRA...")
        
        asignaturas = Asignatura.query.all()
        tareas_creadas = 0
        
        for asignatura in asignaturas[:10]:  # Solo primeras 10 asignaturas
            for i in range(2):  # 2 tareas por asignatura
                tarea = Tarea(
                    titulo=f"Tarea {i+1} - {asignatura.nombre}",
                    descripcion=f"Descripción de la tarea {i+1} para {asignatura.nombre}. Los estudiantes deben completar los ejercicios asignados y entregar el trabajo en la fecha indicada.",
                    fecha_entrega=datetime.now() + timedelta(days=random.randint(7, 30)),
                    asignatura_id=asignatura.id,
                    profesor_id=asignatura.profesor_id,
                    activa=True
                )
                
                db.session.add(tarea)
                tareas_creadas += 1
        
        db.session.commit()
        print(f"   ✅ {tareas_creadas} tareas de muestra creadas")

def mostrar_estadisticas(app):
    """Mostrar estadísticas finales"""
    with app.app_context():
        print("\n📊 ESTADÍSTICAS FINALES:")
        print(f"   👥 Usuarios totales: {Usuario.query.count()}")
        print(f"   👨‍🏫 Profesores: {Usuario.query.filter_by(role='profesor').count()}")
        print(f"   🎓 Estudiantes: {Usuario.query.filter_by(role='estudiante').count()}")
        print(f"   📚 Cursos: {Curso.query.count()}")
        print(f"   📖 Asignaturas: {Asignatura.query.count()}")
        print(f"   🕐 Horarios: {Horario.query.count()}")
        print(f"   📝 Tareas: {Tarea.query.count()}")

def main():
    """Función principal para poblar la base de datos"""
    print("🎓 POBLANDO BASE DE DATOS - COLEGIO COLOMBIA")
    print("=" * 60)
    
    try:
        # Reiniciar base de datos
        app = reiniciar_base_datos()
        
        # Crear estructura básica
        crear_cursos(app)
        crear_profesores(app)
        crear_estudiantes(app, num_estudiantes=50)
        crear_asignaturas(app)
        crear_horarios(app)
        crear_tareas_muestra(app)
        
        # Mostrar estadísticas
        mostrar_estadisticas(app)
        
        print(f"\n✅ BASE DE DATOS POBLADA EXITOSAMENTE")
        print(f"🎯 El Colegio Colombia está listo para funcionar")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()