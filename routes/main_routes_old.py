from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import Usuario
from forms import LoginForm
from extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/test')
def test():
    """Ruta de prueba"""
    return "¡El servidor Flask está funcionando correctamente!"

@main_bp.route('/')
def index():
    """Página de inicio"""
    if current_user.is_authenticated:
        # Redirigir según el rol del usuario
        if current_user.es_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.es_profesor:
            return redirect(url_for('profesor.dashboard'))
        elif current_user.es_estudiante:
            return redirect(url_for('estudiante.dashboard'))
    # Usar el login principal con WTForms que tiene CSRF
    return redirect(url_for('main.login'))

@main_bp.route('/simple-login', methods=['GET', 'POST'])
def simple_login():
    """Inicio de sesión simplificado sin WTForms"""
    print(f"DEBUG: Simple login request - Method: {request.method}")
    
    if current_user.is_authenticated:
        print("DEBUG: Usuario ya autenticado, redirigiendo")
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember_me = bool(request.form.get('remember_me'))
        
        print(f"DEBUG: Datos recibidos - Email: {email}, Password: {'*' * len(password)}, Remember: {remember_me}")
        
        if email and password:
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario:
                print(f"DEBUG: Usuario encontrado: {usuario.nombre_completo}, Rol: {usuario.rol}, Activo: {usuario.activo}")
                
                if usuario.check_password(password):
                    print("DEBUG: Contraseña correcta")
                    
                    if usuario.activo:
                        login_user(usuario, remember=remember_me)
                        print(f"DEBUG: Login exitoso! Redirigiendo según rol: {usuario.rol}")
                        
                        # Redirigir según el rol
                        if usuario.es_admin:
                            next_page = url_for('admin.dashboard')
                            print(f"DEBUG: Redirigiendo a admin dashboard: {next_page}")
                        elif usuario.es_profesor:
                            next_page = url_for('profesor.dashboard')
                            print(f"DEBUG: Redirigiendo a profesor dashboard: {next_page}")
                        elif usuario.es_estudiante:
                            next_page = url_for('estudiante.dashboard')
                            print(f"DEBUG: Redirigiendo a estudiante dashboard: {next_page}")
                        else:
                            next_page = url_for('main.index')
                            print(f"DEBUG: Redirigiendo a index: {next_page}")
                        
                        return redirect(next_page)
                    else:
                        print("DEBUG: Usuario inactivo")
                        flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
                else:
                    print("DEBUG: Contraseña incorrecta")
                    flash('Email o contraseña incorrectos', 'error')
            else:
                print(f"DEBUG: Usuario no encontrado: {email}")
                flash('Email o contraseña incorrectos', 'error')
        else:
            print("DEBUG: Email o contraseña vacíos")
            flash('Por favor ingresa email y contraseña', 'error')
    
    return render_template('auth/simple_login.html', title='Iniciar Sesión')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Inicio de sesión"""
    print(f"DEBUG: Login request - Method: {request.method}")
    
    if current_user.is_authenticated:
        print("DEBUG: Usuario ya autenticado, redirigiendo")
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if request.method == 'POST':
        print(f"DEBUG: POST request received")
        print(f"DEBUG: Form data: email={request.form.get('email')}, password={'*' * len(request.form.get('password', ''))}")
        print(f"DEBUG: Form validate_on_submit: {form.validate_on_submit()}")
        print(f"DEBUG: Form errors: {form.errors}")
        
        if form.validate_on_submit():
            email = form.email.data.strip().lower()
            password = form.password.data
            
            print(f"DEBUG: Buscando usuario con email: {email}")
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario:
                print(f"DEBUG: Usuario encontrado: {usuario.nombre_completo}, Rol: {usuario.rol}, Activo: {usuario.activo}")
                if usuario.check_password(password):
                    print("DEBUG: Contraseña correcta")
                    if usuario.activo:
                        login_user(usuario, remember=form.remember_me.data)
                        print(f"DEBUG: Usuario logueado exitosamente, redirigiendo según rol: {usuario.rol}")
                        
                        # Redirigir según el rol
                        if usuario.es_admin:
                            next_page = url_for('admin.dashboard')
                        elif usuario.es_profesor:
                            next_page = url_for('profesor.dashboard')
                        elif usuario.es_estudiante:
                            next_page = url_for('estudiante.dashboard')
                        else:
                            next_page = url_for('main.index')
                        
                        print(f"DEBUG: Redirigiendo a: {next_page}")
                        return redirect(next_page)
                    else:
                        print("DEBUG: Usuario inactivo")
                        flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
                else:
                    print("DEBUG: Contraseña incorrecta")
                    flash('Email o contraseña incorrectos', 'error')
            else:
                print(f"DEBUG: Usuario no encontrado con email: {email}")
                flash('Email o contraseña incorrectos', 'error')
        else:
            print(f"DEBUG: Validación falló, errores: {form.errors}")
    
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('main.index'))