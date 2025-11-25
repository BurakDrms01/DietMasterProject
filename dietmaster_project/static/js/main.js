document.addEventListener('DOMContentLoaded', function() {
    // Toast Container Creation with improved positioning
    if (!document.getElementById('toast-container')) {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';  // Higher z-index to ensure visibility
        container.style.marginTop = '70px';  // Below navbar
        document.body.appendChild(container);
    }

    // HTMX Event Listener for Toast (legacy - kept for backward compatibility)
    document.body.addEventListener('showMessage', function(evt) {
        const data = evt.detail;
        const type = data.type || 'info';
        const message = data.message || '';
        if (message) {
            showToast(type, message);
        }
    });

    // REMOVED: Generic 'toast' event listener - was causing double toasts!
    // HTMX automatically triggers events from HX-Trigger JSON keys
    // We handle toast in htmx:afterRequest instead to avoid duplicates

    // Handle Django Messages (if any exist in a specific script tag or data attribute)
    const djangoMessages = document.querySelectorAll('.django-message-data');
    djangoMessages.forEach(msg => {
        const type = msg.dataset.type;
        const message = msg.dataset.message;
        showToast(type, message);
        msg.remove();
    });

    // --- HTMX Loading States ---
    document.body.addEventListener('htmx:beforeRequest', function(evt) {
        // Disable the element that triggered the request
        const target = evt.detail.elt;
        if (target.tagName === 'BUTTON' || target.tagName === 'A' || target.tagName === 'INPUT') {
            target.classList.add('disabled');
            target.setAttribute('disabled', 'true');
            
            // Optional: Add spinner if it's a button
            if (target.tagName === 'BUTTON' && !target.querySelector('.spinner-border')) {
                const originalText = target.innerHTML;
                target.dataset.originalText = originalText;
                // Check if button has width to prevent resizing
                const width = target.offsetWidth;
                target.style.width = `${width}px`;
                target.innerHTML = `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>`;
            }
        }
    });

    document.body.addEventListener('htmx:afterRequest', function(evt) {
        // Re-enable the element
        const target = evt.detail.elt;
        if (target.tagName === 'BUTTON' || target.tagName === 'A' || target.tagName === 'INPUT') {
            target.classList.remove('disabled');
            target.removeAttribute('disabled');
            
            // Restore original text
            if (target.dataset.originalText) {
                target.innerHTML = target.dataset.originalText;
                target.style.width = ''; // Reset width
                delete target.dataset.originalText;
            }
        }

        // BUGFIX: Parse HX-Trigger header manually (ONLY source of truth for toast)
        const xhr = evt.detail.xhr;
        if (xhr) {
            const triggerHeader = xhr.getResponseHeader('HX-Trigger');
            if (triggerHeader) {
                try {
                    const triggers = JSON.parse(triggerHeader);
                    
                    // Handle toast notification - SINGLE source of truth
                    if (triggers.toast) {
                        showToast(triggers.toast.type, triggers.toast.message);
                    }
                    
                    // BUGFIX: Handle appointment removal (cancelled/rejected)
                    if (triggers.removeAppointment) {
                        // Element already removed by HTMX swap with empty content
                        // Just show visual feedback
                        console.log('Appointment removed:', triggers.removeAppointment);
                    }
                    
                    // BUGFIX: Update dashboard widget when today's appointment is cancelled
                    if (triggers.updateDashboardWidget) {
                        const widgetContainer = document.getElementById('bugunku-randevu-widget');
                        if (widgetContainer) {
                            // Fetch updated widget HTML
                            fetch('/widget/bugunku-randevu/', {
                                headers: {
                                    'HX-Request': 'true'
                                }
                            })
                            .then(response => response.text())
                            .then(html => {
                                widgetContainer.innerHTML = html;
                                // Add subtle animation
                                widgetContainer.style.animation = 'successPulse 0.5s ease-out';
                            })
                            .catch(err => console.error('Widget update failed:', err));
                        }
                    }
                    
                    // BUGFIX: Handle modal close after appointment creation
                    if (triggers.closeModal) {
                        const modal = document.querySelector('.modal.show');
                        if (modal) {
                            const modalInstance = bootstrap.Modal.getInstance(modal);
                            if (modalInstance) {
                                // Add success pulse animation to modal before closing
                                modal.querySelector('.modal-content').style.animation = 'successPulse 0.5s ease-out';
                                
                                // Wait for toast to be visible and animation to complete
                                setTimeout(function() {
                                    modalInstance.hide();
                                    // After modal is fully hidden, refresh the page
                                    modal.addEventListener('hidden.bs.modal', function() {
                                        window.location.reload();
                                    }, { once: true });
                                }, 1500);  // Increased to 1.5s for better UX
                            }
                        } else {
                            // Fallback if modal not found - wait before reload
                            setTimeout(function() {
                                window.location.reload();
                            }, 1500);
                        }
                    }
                } catch (e) {
                    console.error('Failed to parse HX-Trigger header:', e);
                }
            }
        }
    });

    // Handle HTMX Errors
    document.body.addEventListener('htmx:responseError', function(evt) {
        showToast('error', 'Bir hata oluştu. Lütfen tekrar deneyin.');
    });

    // --- Handle Bootstrap re-initialization after HTMX Swap ---
    document.body.addEventListener('htmx:afterSwap', function(evt) {
        // BUGFIX: Re-initialize Bootstrap dropdowns after HTMX swap to fix user menu
        // This prevents the "user menu not responding" issue after appointment creation
        const dropdowns = evt.detail.target.querySelectorAll('[data-bs-toggle="dropdown"]');
        dropdowns.forEach(dropdown => {
            // Dispose old instance if exists
            const oldInstance = bootstrap.Dropdown.getInstance(dropdown);
            if (oldInstance) {
                oldInstance.dispose();
            }
            // Create new instance
            new bootstrap.Dropdown(dropdown);
        });
    });
});

function showToast(type, message) {
    const container = document.getElementById('toast-container');
    
    // Icon and Class mapping
    let icon = 'bi-info-circle';
    let bgClass = 'text-bg-primary';
    let iconBg = '#3b82f6';
    
    // Map Django message tags to Bootstrap classes
    if (type === 'error') type = 'danger';
    if (type === 'debug') type = 'secondary';

    switch(type) {
        case 'success':
            icon = 'bi-check-circle-fill';
            bgClass = 'text-bg-success';
            iconBg = '#10b981';
            // Play subtle success sound
            playSuccessSound();
            break;
        case 'error':
        case 'danger':
            icon = 'bi-exclamation-circle-fill';
            bgClass = 'text-bg-danger';
            iconBg = '#ef4444';
            break;
        case 'warning':
            icon = 'bi-exclamation-triangle-fill';
            bgClass = 'text-bg-warning';
            iconBg = '#f59e0b';
            break;
        case 'info':
        default:
            icon = 'bi-info-circle-fill';
            bgClass = 'text-bg-info';
            iconBg = '#3b82f6';
            break;
    }

    const toastId = 'toast-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center ${bgClass} border-0 mb-2 shadow-lg" 
             role="alert" aria-live="assertive" aria-atomic="true" 
             style="min-width: 350px; animation: slideInRight 0.3s ease-out;">
            <div class="d-flex">
                <div class="toast-body d-flex align-items-center py-3">
                    <i class="bi ${icon} fs-4 me-3" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));"></i>
                    <div class="fw-semibold" style="font-size: 0.95rem;">${message}</div>
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" 
                        data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-progress" style="height: 4px; background: rgba(255,255,255,0.3); position: relative; overflow: hidden;">
                <div class="progress-bar" style="height: 100%; background: rgba(255,255,255,0.8); width: 100%; animation: shrink 8s linear;"></div>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { 
        delay: 8000,
        autohide: true 
    });
    toast.show();
    
    // Remove from DOM after hidden
    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

// Success sound effect (subtle)
function playSuccessSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 800;
        oscillator.type = 'sine';
        
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.1);
    } catch (e) {
        // Silently fail if audio not supported
    }
}
