#!/usr/bin/env python3
"""
Script de inicialización de la base de datos para la Plataforma Estudiantil
Crea las tablas y datos iniciales necesarios para el funcionamiento del sistema
"""

from app import create_app, db
from models import Usuario, Curso, Asignatura, Horario
from datetime import datetime, time
import os

def init_database():
    """Inicializar base de datos con estructura y datos de ejemplo"""
    
    app = create_app()
    
    with app.app_context():
        print("🗄️  Creando tablas de base de datos...")
        
        # Eliminar todas las tablas existentes y recrearlas
        db.drop_all()
        db.create_all()
        
        print("✅ Tablas creadas correctamente")
        
        # Crear usuario administrador por defecto
        print("\n👤 Creando usuarios por defecto...")
        
        # Administrador
        admin = Usuario(
            nombres="Administrador",
            apellidos="Sistema",
            email="admin@colegiocolombia.edu.co",
            tipo_documento="C.C.",
            numero_documento="12345678",
            telefono="3001234567",
            direccion="Cra 10 # 20-30, Bogotá",
            role="admin"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Profesores de ejemplo
        profesores = [
            {
                "nombre": "María", "apellido": "García",
                "email": "maria.garcia@colegiocolombia.edu.co",
                "documento": "23456789", "telefono": "3009876543"
            },
            {
                "nombre": "Carlos", "apellido": "Rodríguez", 
                "email": "carlos.rodriguez@colegiocolombia.edu.co",
                "documento": "34567890", "telefono": "3008765432"
            },
            {
                "nombre": "Ana", "apellido": "López",
                "email": "ana.lopez@colegiocolombia.edu.co", 
                "documento": "45678901", "telefono": "3007654321"
            },
            {
                "nombre": "Luis", "apellido": "Martínez",
                "email": "luis.martinez@colegiocolombia.edu.co",
                "documento": "56789012", "telefono": "3006543210"
            },
            {
                "nombre": "Elena", "apellido": "Sánchez",
                "email": "elena.sanchez@colegiocolombia.edu.co",
                "documento": "67890123", "telefono": "3005432109"
            }
        ]
        
        profesores_objs = []
        for prof_data in profesores:
            profesor = Usuario(
                nombres=prof_data["nombre"],
                apellidos=prof_data["apellido"],
                email=prof_data["email"],
                tipo_documento="C.C.",
                numero_documento=prof_data["documento"],
                telefono=prof_data["telefono"],
                direccion="Dirección de ejemplo",
                role="profesor"
            )
            profesor.set_password("profesor123")
            profesores_objs.append(profesor)
            db.session.add(profesor)
        
        # Estudiantes de ejemplo
        estudiantes_data = [
            # Estudiantes de 6º
            {"nombre": "Juan", "apellido": "Pérez", "documento": "1001234567", "grado": "6º"},
            {"nombre": "Sofía", "apellido": "González", "documento": "1001234568", "grado": "6º"},
            {"nombre": "Diego", "apellido": "Ramírez", "documento": "1001234569", "grado": "6º"},
            
            # Estudiantes de 7º  
            {"nombre": "Camila", "apellido": "Torres", "documento": "1001234570", "grado": "7º"},
            {"nombre": "Andrés", "apellido": "Vargas", "documento": "1001234571", "grado": "7º"},
            {"nombre": "Isabella", "apellido": "Morales", "documento": "1001234572", "grado": "7º"},
            
            # Estudiantes de 8º
            {"nombre": "Santiago", "apellido": "Castro", "documento": "1001234573", "grado": "8º"},
            {"nombre": "Valentina", "apellido": "Herrera", "documento": "1001234574", "grado": "8º"},
            {"nombre": "Mateo", "apellido": "Jiménez", "documento": "1001234575", "grado": "8º"},
            
            # Estudiantes de 9º
            {"nombre": "Mariana", "apellido": "Ruiz", "documento": "1001234576", "grado": "9º"},
            {"nombre": "Sebastián", "apellido": "Mendoza", "documento": "1001234577", "grado": "9º"},
            {"nombre": "Gabriela", "apellido": "Ortiz", "documento": "1001234578", "grado": "9º"},
            
            # Estudiantes de 10º
            {"nombre": "Alejandro", "apellido": "Silva", "documento": "1001234579", "grado": "10º"},
            {"nombre": "Natalia", "apellido": "Ramos", "documento": "1001234580", "grado": "10º"},
            {"nombre": "Daniel", "apellido": "Aguilar", "documento": "1001234581", "grado": "10º"},
            
            # Estudiantes de 11º
            {"nombre": "Andrea", "apellido": "Flores", "documento": "1001234582", "grado": "11º"},
            {"nombre": "Miguel", "apellido": "Vega", "documento": "1001234583", "grado": "11º"},
            {"nombre": "Laura", "apellido": "Delgado", "documento": "1001234584", "grado": "11º"},
        ]
        
        for est_data in estudiantes_data:
            estudiante = Usuario(
                nombres=est_data["nombre"],
                apellidos=est_data["apellido"],
                email=f"{est_data['nombre'].lower()}.{est_data['apellido'].lower()}@estudiante.colegiocolombia.edu.co",
                tipo_documento="T.I.",
                numero_documento=est_data["documento"],
                telefono="3001111111",
                direccion="Dirección de ejemplo",
                role="estudiante"
            )
            estudiante.set_password("estudiante123")
            db.session.add(estudiante)
        
        db.session.commit()
        print(f"✅ Creados {len(profesores)} profesores y {len(estudiantes_data)} estudiantes")
        
        # Crear cursos
        print("\n📚 Creando cursos...")
        
        cursos_data = []
        for grado in ['6º', '7º', '8º', '9º', '10º', '11º']:
            for seccion in ['A', 'B']:
                curso = Curso(
                    grado=grado,
                    seccion=seccion,
                    año_academico=datetime.now().year
                )
                cursos_data.append(curso)
                db.session.add(curso)
        
        db.session.commit()
        print(f"✅ Creados {len(cursos_data)} cursos")
        
        # Asignar estudiantes a cursos
        print("\n👥 Asignando estudiantes a cursos...")
        
        todos_estudiantes = Usuario.query.filter_by(role='estudiante').all()
        todos_cursos = Curso.query.all()
        
        # Mapear estudiantes por grado
        estudiantes_por_grado = {}
        for estudiante in todos_estudiantes:
            # Extraer grado del documento (simplificado)
            grado_map = {
                '1001234567': '6º', '1001234568': '6º', '1001234569': '6º',
                '1001234570': '7º', '1001234571': '7º', '1001234572': '7º',
                '1001234573': '8º', '1001234574': '8º', '1001234575': '8º',
                '1001234576': '9º', '1001234577': '9º', '1001234578': '9º',
                '1001234579': '10º', '1001234580': '10º', '1001234581': '10º',
                '1001234582': '11º', '1001234583': '11º', '1001234584': '11º',
            }
            grado = grado_map.get(estudiante.numero_documento, '6º')
            if grado not in estudiantes_por_grado:
                estudiantes_por_grado[grado] = []
            estudiantes_por_grado[grado].append(estudiante)
        
        # Asignar a cursos
        for grado, estudiantes in estudiantes_por_grado.items():
            cursos_grado = [c for c in todos_cursos if c.grado == grado]
            if cursos_grado:
                curso = cursos_grado[0]  # Asignar todos a sección A por simplicidad
                for estudiante in estudiantes:
                    curso.usuarios.append(estudiante)
        
        db.session.commit()
        print("✅ Estudiantes asignados a cursos")
        
        # Crear asignaturas
        print("\n📖 Creando asignaturas...")
        
        asignaturas_base = [
            "Matemáticas", "Español", "Ciencias Naturales", "Ciencias Sociales",
            "Inglés", "Educación Física", "Artística", "Informática", 
            "Ética y Valores", "Religión"
        ]
        
        # Asignaturas adicionales por grado
        asignaturas_avanzadas = {
            '9º': ["Química", "Física"],
            '10º': ["Química", "Física", "Filosofía", "Economía"],
            '11º': ["Química", "Física", "Filosofía", "Economía", "Cálculo"]
        }
        
        contador_asignaturas = 0
        for curso in todos_cursos:
            asignaturas_curso = asignaturas_base.copy()
            if curso.grado in asignaturas_avanzadas:
                asignaturas_curso.extend(asignaturas_avanzadas[curso.grado])
            
            for i, nombre_asignatura in enumerate(asignaturas_curso):
                # Asignar profesor (rotar entre los disponibles)
                profesor = profesores_objs[i % len(profesores_objs)]
                
                asignatura = Asignatura(
                    nombre=nombre_asignatura,
                    descripcion=f"Asignatura de {nombre_asignatura} para {curso.grado}{curso.seccion}",
                    curso_id=curso.id,
                    profesor_id=profesor.id
                )
                db.session.add(asignatura)
                contador_asignaturas += 1
        
        db.session.commit()
        print(f"✅ Creadas {contador_asignaturas} asignaturas")
        
        # Crear horarios básicos
        print("\n⏰ Creando horarios de ejemplo...")
        
        # Horas de clase (usando configuración)
        from config import Config
        horas_clase = Config.HORAS_CLASES
        
        contador_horarios = 0
        for curso in todos_cursos:
            asignaturas_curso = Asignatura.query.filter_by(curso_id=curso.id).all()
            
            # Crear horario simple: una asignatura por día/hora
            for dia in range(5):  # Lunes a Viernes
                for i, (hora_inicio, hora_fin) in enumerate(horas_clase[:6]):  # 6 horas por día
                    if i < len(asignaturas_curso):
                        asignatura = asignaturas_curso[i % len(asignaturas_curso)]
                        
                        horario = Horario(
                            dia_semana=dia,
                            hora_inicio=time.fromisoformat(hora_inicio),
                            hora_fin=time.fromisoformat(hora_fin),
                            curso_id=curso.id,
                            asignatura_id=asignatura.id,
                            profesor_id=asignatura.profesor_id,
                            aula=f"Aula {curso.grado}{curso.seccion}-{i+1:02d}"
                        )
                        db.session.add(horario)
                        contador_horarios += 1
        
        db.session.commit()
        print(f"✅ Creados {contador_horarios} horarios")
        
        print("\n🎉 ¡Base de datos inicializada correctamente!")
        print("\n📝 Credenciales de acceso:")
        print("=" * 50)
        print("🔑 ADMINISTRADOR:")
        print("   Email: admin@colegiocolombia.edu.co")
        print("   Contraseña: admin123")
        print("\n👨‍🏫 PROFESORES:")
        print("   Email: [nombre].[apellido]@colegiocolombia.edu.co")
        print("   Contraseña: profesor123")
        print("   Ejemplo: maria.garcia@colegiocolombia.edu.co")
        print("\n🎓 ESTUDIANTES:")
        print("   Email: [nombre].[apellido]@estudiante.colegiocolombia.edu.co")
        print("   Contraseña: estudiante123")
        print("   Ejemplo: juan.perez@estudiante.colegiocolombia.edu.co")
        print("=" * 50)
        
        # Mostrar estadísticas
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   👤 Usuarios totales: {Usuario.query.count()}")
        print(f"   👨‍💼 Administradores: {Usuario.query.filter_by(role='admin').count()}")
        print(f"   👨‍🏫 Profesores: {Usuario.query.filter_by(role='profesor').count()}")
        print(f"   🎓 Estudiantes: {Usuario.query.filter_by(role='estudiante').count()}")
        print(f"   📚 Cursos: {Curso.query.count()}")
        print(f"   📖 Asignaturas: {Asignatura.query.count()}")
        print(f"   ⏰ Horarios: {Horario.query.count()}")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"\n❌ Error al inicializar la base de datos: {str(e)}")
        print("\n🔍 Verificar que:")
        print("   - Las dependencias estén instaladas (pip install -r requirements.txt)")
        print("   - Los permisos de escritura estén disponibles") 
        print("   - No haya otra instancia de la aplicación ejecutándose")
    except KeyboardInterrupt:
        print("\n\n⏹️  Inicialización cancelada por el usuario")