#!/bin/bash

echo "==============================================="
echo "   PLATAFORMA ESTUDIANTIL - COLEGIO COLOMBIA"
echo "==============================================="
echo

# Usar Python del entorno virtual
PYTHON_CMD="/c/Users/angeh/Desktop/proyecto platafroma/.venv/Scripts/python.exe"

# Verificar si Python está disponible
if ! "$PYTHON_CMD" --version &> /dev/null; then
    echo "❌ Error: No se puede acceder al entorno virtual Python"
    echo "Asegúrate de que el entorno virtual está configurado correctamente"
    exit 1
fi

echo "✅ Python detectado correctamente"
"$PYTHON_CMD" --version

echo
echo "📦 Verificando dependencias..."
"$PYTHON_CMD" -m pip install -r requirements.txt > /dev/null 2>&1

echo
echo "🗄️  Verificando base de datos..."
if [ ! -f "instance/database.db" ]; then
    echo "Inicializando base de datos..."
    "$PYTHON_CMD" init_db.py
    if [ $? -ne 0 ]; then
        echo "❌ Error inicializando base de datos"
        exit 1
    fi
else
    echo "✅ Base de datos ya existe"
fi

echo
echo "🚀 Iniciando servidor Flask..."
echo
echo "🌐 La aplicación estará disponible en: http://localhost:5000"
echo
echo "🔑 CREDENCIALES DE ACCESO:"
echo "   👑 Admin: admin@colegiocolombia.edu.co / admin123"
echo "   👨‍🏫 Profesores: [nombre].[apellido]@colegiocolombia.edu.co / profesor123"
echo "   🎓 Estudiantes: [nombre].[apellido]@estudiante.colegiocolombia.edu.co / estudiante123"
echo
echo "💡 Presiona Ctrl+C para detener el servidor"
echo "==============================================="
echo

"$PYTHON_CMD" app.py