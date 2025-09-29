#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verificar correcciones de AttributeError nombres_completo
"""

import re
import os

def verificar_correcciones():
    """Verifica que todas las correcciones se aplicaron correctamente"""
    
    archivos_python = []
    
    # Buscar todos los archivos .py
    for root, dirs, files in os.walk('.'):
        # Excluir directorios de cache
        if '__pycache__' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                archivos_python.append(os.path.join(root, file))
    
    print("🔍 VERIFICANDO CORRECCIONES DE AttributeError")
    print("=" * 60)
    
    errores_encontrados = []
    
    for archivo in archivos_python:
        try:
            with open(archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
                
            # Buscar nombres_completo (incorrecto)
            lineas = contenido.split('\n')
            for i, linea in enumerate(lineas, 1):
                if 'nombres_completo' in linea and '.nombres_completo' in linea:
                    errores_encontrados.append({
                        'archivo': archivo,
                        'linea': i,
                        'contenido': linea.strip()
                    })
                    
        except Exception as e:
            print(f"⚠️ Error leyendo {archivo}: {e}")
    
    if errores_encontrados:
        print("❌ ERRORES ENCONTRADOS:")
        print("-" * 40)
        for error in errores_encontrados:
            print(f"📄 Archivo: {error['archivo']}")
            print(f"📍 Línea {error['linea']}: {error['contenido']}")
            print()
    else:
        print("✅ NO SE ENCONTRARON ERRORES DE nombres_completo")
    
    # Verificar que nombre_completo existe en models.py
    print("\n🔍 VERIFICANDO MODELO Usuario:")
    print("-" * 40)
    
    try:
        with open('./models.py', 'r', encoding='utf-8') as f:
            contenido = f.read()
            
        if 'def nombre_completo(self):' in contenido:
            print("✅ Método nombre_completo definido correctamente en Usuario")
        else:
            print("❌ Método nombre_completo NO encontrado en Usuario")
            
    except Exception as e:
        print(f"⚠️ Error leyendo models.py: {e}")
    
    print("\n" + "=" * 60)
    
    if errores_encontrados:
        print(f"❌ TOTAL ERRORES: {len(errores_encontrados)}")
        print("🔧 REQUIERE CORRECCIÓN")
    else:
        print("✅ TODAS LAS CORRECCIONES APLICADAS CORRECTAMENTE")
        print("🚀 LISTO PARA EJECUTAR SERVIDOR")

if __name__ == "__main__":
    verificar_correcciones()