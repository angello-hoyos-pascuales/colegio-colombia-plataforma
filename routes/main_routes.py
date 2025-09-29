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
                print(f"DEBUG: Usuario encontrado: {usuario.nombre_completo}, Role: {usuario.role}, Activo: {usuario.activo}")
                
                if usuario.activo and usuario.check_password(password):
                    login_user(usuario, remember=remember_me)
                    next_page = request.args.get('next')
                    
                    if next_page and urlparse(next_page).netloc == '':
                        print(f"DEBUG: Login exitoso! Redirigiendo según role: {usuario.role}")
                        return redirect(next_page)
                    else:
                        return redirect(url_for('main.index'))
                else:
                    if not usuario.activo:
                        print("DEBUG: Usuario inactivo")
                        flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
                    else:
                        print("DEBUG: Contraseña incorrecta")
                        flash('Email o contraseña incorrectos.', 'error')
            else:
                print("DEBUG: Usuario no encontrado")
                flash('Email o contraseña incorrectos.', 'error')
        else:
            print("DEBUG: Datos faltantes")
            flash('Por favor completa todos los campos.', 'error')
    
    return render_template('auth/simple_login.html')

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión con WTForms"""
    print(f"DEBUG: Login request - Method: {request.method}")
    
    if current_user.is_authenticated:
        print("DEBUG: Usuario ya autenticado, redirigiendo")
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        password = form.password.data
        remember_me = form.remember_me.data
        
        print(f"DEBUG: Login con WTForms - Email: {email}, Remember: {remember_me}")
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario:
            print(f"DEBUG: Usuario encontrado: {usuario.nombre_completo}, Role: {usuario.role}, Activo: {usuario.activo}")
            
            if usuario.activo and usuario.check_password(password):
                login_user(usuario, remember=remember_me)
                print(f"DEBUG: Usuario logueado exitosamente, redirigiendo según role: {usuario.role}")
                
                next_page = request.args.get('next')
                if next_page and urlparse(next_page).netloc == '':
                    return redirect(next_page)
                else:
                    return redirect(url_for('main.index'))
            else:
                if not usuario.activo:
                    print("DEBUG: Usuario inactivo")
                    flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
                else:
                    print("DEBUG: Contraseña incorrecta")
                    flash('Email o contraseña incorrectos.', 'error')
        else:
            print("DEBUG: Usuario no encontrado en login WTF")
            flash('Email o contraseña incorrectos.', 'error')
    else:
        if form.errors:
            print(f"DEBUG: Errores en el formulario: {form.errors}")
    
    return render_template('auth/login.html', form=form)

@main_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    print(f"DEBUG: Cerrando sesión del usuario: {current_user.nombre_completo}")
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/profile')
@login_required
def profile():
    """Perfil del usuario actual"""
    return render_template('profile.html', usuario=current_user)

@main_bp.route('/about')
def about():
    """Página acerca de"""
    return render_template('about.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard genérico que redirige según el rol"""
    if current_user.es_admin:
        return redirect(url_for('admin.dashboard'))
    elif current_user.es_profesor:
        return redirect(url_for('profesor.dashboard'))
    elif current_user.es_estudiante:
        return redirect(url_for('estudiante.dashboard'))
    else:
        flash('Rol de usuario no reconocido.', 'error')
        return redirect(url_for('main.logout'))

# Manejar errores 404
@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

# Manejar errores 500
@main_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500