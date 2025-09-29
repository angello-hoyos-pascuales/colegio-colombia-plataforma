#!/usr/bin/env python3
"""
Script de inicialización forzada de la base de datos
"""

import os
import sys
import sqlite3

# Cambiar al directorio del proyecto
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def crear_base_datos_forzada():
    print("🔧 INICIALIZACIÓN FORZADA DE BASE DE DATOS")
    print("="*60)
    
    # 1. Eliminar base de datos existente
    archivos_db = ['database.db', 'colegio_colombia.db', 'instance/database.db']
    for archivo in archivos_db:
        if os.path.exists(archivo):
            os.remove(archivo)
            print(f"   🗑️ Eliminado: {archivo}")
    
    # 2. Crear directorio instance si no existe
    if not os.path.exists('instance'):
        os.makedirs('instance')
        print("   📁 Directorio instance creado")
    
    # 3. Importar y crear app
    try:
        from app import create_app
        from extensions import db
        from models import Usuario, Curso, Asignatura, Horario
        
        print("   ✅ Módulos importados correctamente")
        
        app = create_app()
        
        with app.app_context():
            print("   🗄️ Creando tablas...")
            db.create_all()
            
            # Verificar que las tablas se crearon
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            tablas = inspector.get_table_names()
            print(f"   ✅ Tablas creadas: {len(tablas)} tablas")
            
            # Crear admin básico
            admin = Usuario(
                nombres="Admin",
                apellidos="Colegio",
                email="admin@colegiocolombia.edu.co",
                tipo_documento="C.C.",
                numero_documento="12345678",
                role="admin"
            )
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()
            
            print("   ✅ Usuario admin creado")
            
            # Verificar archivo de base de datos
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            print(f"   📍 URI de BD: {db_uri}")
            
            if 'sqlite:///' in db_uri:
                db_path = db_uri.replace('sqlite:///', '')
                if os.path.exists(db_path):
                    size = os.path.getsize(db_path)
                    print(f"   ✅ Archivo BD: {db_path} ({size} bytes)")
                else:
                    print(f"   ❌ Archivo BD no encontrado: {db_path}")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("="*60)
    print("✅ INICIALIZACIÓN COMPLETADA")
    return True

def probar_servidor():
    print("\n🧪 PROBANDO SERVIDOR...")
    try:
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/')
            print(f"   ✅ Servidor responde: {response.status_code}")
            
        print("   🚀 Listo para iniciar servidor")
        return True
        
    except Exception as e:
        print(f"   ❌ Error probando servidor: {e}")
        return False

if __name__ == "__main__":
    if crear_base_datos_forzada():
        if probar_servidor():
            print("\n🎯 TODO LISTO - Ejecuta: python app.py")
        else:
            print("\n❌ Problema con el servidor")
    else:
        print("\n❌ Problema con la base de datos")