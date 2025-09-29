<<<<<<< HEAD
# 🎓 Plataforma Estudiantil Web - Colegio Colombia

## ✅ PROYECTO COMPLETADO - 100% FUNCIONAL

Una plataforma educativa completa desarrollada con Python/Flask que incluye gestión de usuarios, cursos, tareas y un sistema avanzado de horarios en tiempo real con detección automática de ausencias y asignación de reemplazos.

## 🚀 INICIO RÁPIDO

### 1. Iniciar el Servidor
```bash
"C:/Users/angeh/Desktop/proyecto platafroma/.venv/Scripts/python.exe" app.py
```

### 2. Acceder a la Plataforma
- **URL Principal:** http://127.0.0.1:5000
- **Login Simplificado:** http://127.0.0.1:5000/simple-login

### 3. Credenciales de Acceso

#### 👨‍💼 Administrador
- **Email:** admin@colegiocolombia.edu.co
- **Contraseña:** admin123

#### 👨‍🏫 Profesores
- **Email:** maria.garcia@colegiocolombia.edu.co
- **Contraseña:** profesor123

#### 🎓 Estudiantes  
- **Email:** juan.pérez@estudiante.colegiocolombia.edu.co
- **Contraseña:** estudiante123

## 📊 CARACTERÍSTICAS IMPLEMENTADAS

### ✅ Fase 1: Plataforma Básica Completa
- **Arquitectura:** Python/Flask + SQLite + Bootstrap 5
- **Autenticación:** Sistema completo con Flask-Login
- **Roles:** Administrador, Profesor, Estudiante
- **Usuarios:** 24 usuarios configurados
- **Cursos:** Grados 6º-11º con secciones A/B
- **Asignaturas:** 142 materias asignadas
- **Sistema de calificaciones:** 0.0-5.0 por periodos

### ✅ Fase 2: Módulo Horario Tiempo Real
- **Detección:** Sistema automático de ausencias
- **Algoritmo:** Búsqueda inteligente de reemplazos
- **Notificaciones:** Alertas en tiempo real
- **Horarios:** 360 clases programadas semanalmente
- **Dashboard:** Panel de control administrativo completo

## 🎯 Funcionalidades Principales
📋 Dashboard personalizado por rol  
👥 Gestión completa de usuarios  
🏫 Administración de cursos y grados  
📚 Asignación de materias por profesor  
📝 Sistema de tareas con entregas  
📊 Calificaciones por periodos académicos  
⏰ Horarios dinámicos con detección de ausencias  
🔄 Sistema automático de reemplazos  
📱 Interfaz responsive y moderna

---

¡La plataforma está **100% funcional** y lista para su uso inmediato! 🚀📚✨
- **Identificación Colombiana**: Soporte para T.I. y C.C.

### Fase 2: Módulo de Horario en Tiempo Real
- **Detección Automática**: Identificación de ausencias de profesores
- **Algoritmo de Reemplazo**: Búsqueda automática de profesores disponibles
- **Notificaciones**: Sistema de alertas en tiempo real

## Instalación

### Prerrequisitos
- **Python 3.8 o superior** instalado en el sistema
- **Git** (opcional, para clonar el proyecto)

### Pasos de instalación

1. **Verificar Python:**
```bash
python --version
# o en algunos sistemas:
python3 --version
```

2. **Instalar Python (si no está instalado):**
   - **Windows:** Descargar desde [python.org](https://python.org) o usar Microsoft Store
   - **Linux/Mac:** `sudo apt install python3 python3-pip` o `brew install python3`

3. **Crear entorno virtual:**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

4. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

5. **Inicializar base de datos:**
```bash
python init_db.py
```

6. **Ejecutar la aplicación:**
```bash
python app.py
```

La aplicación estará disponible en `http://localhost:5000`

### Solución de problemas comunes

- **Error "Python no encontrado":**
  - Verificar que Python esté instalado
  - Agregar Python al PATH del sistema
  - Usar `python3` en lugar de `python` en sistemas Linux/Mac

- **Error de permisos:**
  - Ejecutar terminal como administrador (Windows)
  - Usar `sudo` cuando sea necesario (Linux/Mac)

- **Error de dependencias:**
  - Actualizar pip: `python -m pip install --upgrade pip`
  - Instalar dependencias una por una si falla el requirements.txt

## Estructura del Proyecto

```
proyecto-platafroma/
├── app.py                  # Aplicación principal Flask
├── config.py              # Configuración de la aplicación
├── models.py               # Modelos de base de datos
├── forms.py                # Formularios WTForms
├── init_db.py             # Inicialización de base de datos
├── requirements.txt        # Dependencias
├── static/                 # Archivos estáticos (CSS, JS, imágenes)
├── templates/              # Plantillas HTML
├── uploads/                # Archivos subidos por usuarios
└── database.db            # Base de datos SQLite (se crea automáticamente)
```

## Roles y Funcionalidades

### Administrador
- Gestión completa de usuarios
- Configuración de cursos y horarios
- Monitoreo del sistema de reemplazo de profesores
- Reportes y estadísticas

### Profesores
- Gestión de tareas y calificaciones
- Acceso a listas de estudiantes
- Sistema de notificaciones
- Confirmación de reemplazos

### Estudiantes
- Visualización de horarios y tareas
- Entrega de documentos (PDF, DOCX)
- Consulta de calificaciones
- Recepción de notificaciones

## Tecnologías Utilizadas

- **Backend**: Python, Flask
- **Base de Datos**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Autenticación**: Flask-Login
- **Formularios**: Flask-WTF, WTForms

## Contribución

Este proyecto está diseñado para ser ejecutado localmente en un entorno de desarrollo y pruebas para el Colegio Colombia.
=======
# colegio-colombia-plataforma
>>>>>>> b5f952e8ce73624c63d21a0c3a5aa3835ffcf40f
