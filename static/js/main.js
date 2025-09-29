// JavaScript principal para la Plataforma Estudiantil

document.addEventListener('DOMContentLoaded', function() {
    
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts después de 5 segundos
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            if (bsAlert) {
                bsAlert.close();
            }
        }, 5000);
    });

    // Confirmación para acciones destructivas
    const deleteButtons = document.querySelectorAll('.btn-delete, .btn-danger[data-action="delete"]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const message = this.getAttribute('data-message') || '¿Estás seguro de que deseas eliminar este elemento?';
            if (confirm(message)) {
                if (this.tagName === 'A') {
                    window.location.href = this.href;
                } else if (this.tagName === 'BUTTON' && this.form) {
                    this.form.submit();
                }
            }
        });
    });

    // Validación de fechas en formularios
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // Establecer fecha mínima como hoy para fechas futuras
        if (input.name.includes('entrega') || input.name.includes('vencimiento')) {
            const today = new Date().toISOString().split('T')[0];
            input.min = today;
        }
    });

    // Sistema de tiempo real para horarios
    if (document.getElementById('tiempo-real-container')) {
        actualizarTiempoReal();
        setInterval(actualizarTiempoReal, 30000); // Actualizar cada 30 segundos
    }

    // Búsqueda en tiempo real para tablas
    const searchInputs = document.querySelectorAll('.search-input');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const tableBody = document.querySelector(this.getAttribute('data-target'));
            if (tableBody) {
                const rows = tableBody.querySelectorAll('tr');
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    row.style.display = text.includes(searchTerm) ? '' : 'none';
                });
            }
        });
    });

    // Contador de caracteres para textareas
    const textareas = document.querySelectorAll('textarea[maxlength]');
    textareas.forEach(function(textarea) {
        const maxLength = textarea.getAttribute('maxlength');
        const counter = document.createElement('small');
        counter.className = 'form-text text-muted character-counter';
        textarea.parentNode.appendChild(counter);
        
        function updateCounter() {
            const remaining = maxLength - textarea.value.length;
            counter.textContent = `${remaining} caracteres restantes`;
            counter.className = `form-text ${remaining < 50 ? 'text-warning' : 'text-muted'} character-counter`;
        }
        
        updateCounter();
        textarea.addEventListener('input', updateCounter);
    });

    // Previsualización de archivos
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const preview = document.getElementById(input.id + '-preview');
                if (preview) {
                    const fileInfo = `
                        <div class="alert alert-info">
                            <i class="fas fa-file me-2"></i>
                            <strong>${file.name}</strong><br>
                            <small>Tamaño: ${formatFileSize(file.size)}</small>
                        </div>
                    `;
                    preview.innerHTML = fileInfo;
                }
            }
        });
    });
});

// Función para actualizar el estado en tiempo real
function actualizarTiempoReal() {
    fetch('/horario/api/estado_actual')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.log(data.error);
                return;
            }
            
            // Actualizar hora actual
            const horaElement = document.getElementById('hora-actual');
            if (horaElement) {
                horaElement.textContent = data.hora_actual;
            }
            
            // Actualizar clase actual
            const claseActualElement = document.getElementById('clase-actual');
            if (claseActualElement && data.clase_actual) {
                let claseHtml = `
                    <div class="horario-item">
                        <div class="horario-hora">${data.clase_actual.hora_inicio} - ${data.clase_actual.hora_fin}</div>
                        <div class="horario-asignatura">${data.clase_actual.asignatura}</div>
                        <div class="horario-profesor">
                            ${data.clase_actual.tiene_reemplazo ? 
                                `<span class="text-warning"><i class="fas fa-exchange-alt me-1"></i>Reemplazo: ${data.clase_actual.profesor_reemplazo}</span>` :
                                data.clase_actual.profesor
                            }
                        </div>
                        <div class="text-muted">
                            <small><i class="fas fa-users me-1"></i>${data.clase_actual.curso}</small>
                            ${data.clase_actual.aula ? `<small class="ms-2"><i class="fas fa-door-open me-1"></i>${data.clase_actual.aula}</small>` : ''}
                        </div>
                    </div>
                `;
                claseActualElement.innerHTML = claseHtml;
            }
            
            // Actualizar próxima clase
            const proximaClaseElement = document.getElementById('proxima-clase');
            if (proximaClaseElement && data.proxima_clase) {
                let proximaHtml = `
                    <div class="horario-item">
                        <div class="horario-hora">${data.proxima_clase.hora_inicio} - ${data.proxima_clase.hora_fin}</div>
                        <div class="horario-asignatura">${data.proxima_clase.asignatura}</div>
                        <div class="horario-profesor">${data.proxima_clase.profesor}</div>
                        <div class="text-muted">
                            <small><i class="fas fa-users me-1"></i>${data.proxima_clase.curso}</small>
                            ${data.proxima_clase.aula ? `<small class="ms-2"><i class="fas fa-door-open me-1"></i>${data.proxima_clase.aula}</small>` : ''}
                        </div>
                    </div>
                `;
                proximaClaseElement.innerHTML = proximaHtml;
            }
            
            // Actualizar indicador de cambios
            const cambiosElement = document.getElementById('cambios-confirmados');
            if (cambiosElement) {
                cambiosElement.textContent = data.cambios_confirmados || 0;
                if (data.cambios_confirmados > 0) {
                    cambiosElement.parentElement.classList.add('text-warning');
                }
            }
        })
        .catch(error => {
            console.error('Error al actualizar tiempo real:', error);
        });
}

// Función para formatear el tamaño de archivo
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Función para confirmar reemplazos (admin)
function confirmarReemplazos() {
    const checkboxes = document.querySelectorAll('input[name="reemplazo_seleccionado"]:checked');
    const reemplazos = Array.from(checkboxes).map(cb => ({
        horario_id: cb.getAttribute('data-horario-id'),
        profesor_ausente_id: cb.getAttribute('data-profesor-ausente'),
        profesor_reemplazo_id: cb.getAttribute('data-profesor-reemplazo'),
        fecha_ausencia: cb.getAttribute('data-fecha')
    }));
    
    if (reemplazos.length === 0) {
        alert('Selecciona al menos un reemplazo para confirmar');
        return;
    }
    
    if (!confirm(`¿Confirmar ${reemplazos.length} reemplazo(s)?`)) {
        return;
    }
    
    fetch('/admin/confirmar_reemplazos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrf_token]').value
        },
        body: JSON.stringify({ reemplazos: reemplazos })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.message);
            location.reload();
        } else {
            alert('Error al confirmar reemplazos');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

// Función para calcular promedio automáticamente
function calcularPromedio() {
    const notas = document.querySelectorAll('.nota-input');
    let suma = 0;
    let count = 0;
    
    notas.forEach(function(input) {
        const valor = parseFloat(input.value);
        if (!isNaN(valor) && valor > 0) {
            suma += valor;
            count++;
        }
    });
    
    const promedio = count > 0 ? (suma / count).toFixed(2) : '0.00';
    const promedioElement = document.getElementById('promedio-calculado');
    if (promedioElement) {
        promedioElement.textContent = promedio;
        
        // Cambiar color según el promedio
        promedioElement.className = 'nota ';
        if (promedio >= 4.5) {
            promedioElement.classList.add('excelente');
        } else if (promedio >= 4.0) {
            promedioElement.classList.add('buena');
        } else if (promedio >= 3.0) {
            promedioElement.classList.add('regular');
        } else {
            promedioElement.classList.add('mala');
        }
    }
}

// Utilidades para fechas
function formatearFecha(fecha) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        weekday: 'long'
    };
    return new Date(fecha).toLocaleDateString('es-ES', options);
}

function diasHastaVencimiento(fechaVencimiento) {
    const hoy = new Date();
    const vencimiento = new Date(fechaVencimiento);
    const diffTime = vencimiento - hoy;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
}