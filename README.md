# 🎓 Colegio Colombia - Plataforma Educativa

Una plataforma web completa para la gestión educativa desarrollada con Flask y SQLite.

## ✨ Características

- **Sistema de Usuarios**: Administradores, profesores y estudiantes
- **Gestión de Cursos**: Grados 6º a 11º con secciones A y B  
- **Calificaciones**: Sistema completo por períodos académicos
- **Horarios**: Gestión de horarios y asignaturas
- **Dashboard**: Paneles personalizados por rol de usuario

## 🚀 Instalación

### Prerrequisitos
- Python 3.8+
- pip

### Pasos de instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/angello-hoyos-pascuales/colegio-colombia-plataforma.git
cd colegio-colombia-plataforma
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Inicializar base de datos**
```bash
python init_db.py
python poblar_colegio.py
```

5. **Ejecutar aplicación**
```bash
python app.py
```

La aplicación estará disponible en: http://127.0.0.1:5000

## 🔑 Credenciales por Defecto

### Administrador
- **Email**: admin@colegiocolombia.edu.co
- **Contraseña**: admin123

### Profesor (ejemplo)
- **Email**: gonzalo.torres@colegiocolombia.edu.co
- **Contraseña**: profesor123

### Estudiante (ejemplo)
- **Email**: jessica.sanchez@estudiante.colegiocolombia.edu.co
- **Contraseña**: estudiante123

## 📊 Datos Incluidos

La plataforma viene pre-poblada con:
- 👥 **63 usuarios** (1 admin, 14 profesores, 48 estudiantes)
- 📚 **12 cursos** distribuidos en 6 grados
- 📖 **112 asignaturas** con profesores asignados
- 📊 **1,344 calificaciones** de 3 períodos académicos
- 🕐 **289 horarios** académicos

## 💻 Tecnologías

- **Backend**: Python Flask 3.0
- **Base de datos**: SQLite con SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Autenticación**: Flask-Login

## 📁 Estructura del Proyecto

```
colegio-colombia-plataforma/
├── app.py              # Aplicación principal Flask
├── models.py           # Modelos de base de datos
├── forms.py            # Formularios WTF
├── config.py           # Configuración
├── init_db.py          # Inicializador de BD
├── poblar_colegio.py   # Datos de ejemplo
├── requirements.txt    # Dependencias
├── static/             # CSS, JS, imágenes
├── templates/          # Plantillas HTML
└── routes/             # Rutas organizadas por módulo
```

## 🌟 Funcionalidades Principales

### Para Administradores
- Dashboard con estadísticas generales
- Gestión completa de usuarios
- Configuración de cursos y asignaturas
- Supervisión de horarios

### Para Profesores
- Panel de control personalizado
- Gestión de asignaturas asignadas
- Creación y calificación de tareas
- Registro de calificaciones

### Para Estudiantes
- Vista de cursos y horarios
- Acceso a tareas y entregas
- Consulta de calificaciones
- Seguimiento del progreso académico

## 🚀 Despliegue

Para producción, considera:
- Usar un servidor WSGI como Gunicorn
- Configurar una base de datos más robusta (PostgreSQL)
- Implementar HTTPS
- Configurar variables de entorno para credenciales

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

**Desarrollado para el Colegio Colombia** 🇨🇴