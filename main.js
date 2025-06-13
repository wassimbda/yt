// YouTube Title Analyzer - Main JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initializeFormValidation();
    initializeTooltips();
    initializeAnimations();
    initializeCounters();
    initializeCharts();
});

// Form validation and enhancement
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Real-time validation for channel input
    const channelInput = document.getElementById('channel_input');
    if (channelInput) {
        channelInput.addEventListener('input', function() {
            validateChannelInput(this.value);
        });
        
        channelInput.addEventListener('blur', function() {
            this.value = formatChannelInput(this.value);
        });
    }

    // Real-time validation for title input
    const titleInput = document.getElementById('title');
    if (titleInput) {
        titleInput.addEventListener('input', function() {
            updateTitleMetrics(this.value);
        });
    }
}

// Validate channel input
function validateChannelInput(input) {
    const inputElement = document.getElementById('channel_input');
    const isValid = isValidChannelInput(input);
    
    if (input.length > 0) {
        if (isValid) {
            inputElement.classList.remove('is-invalid');
            inputElement.classList.add('is-valid');
        } else {
            inputElement.classList.remove('is-valid');
            inputElement.classList.add('is-invalid');
        }
    } else {
        inputElement.classList.remove('is-invalid', 'is-valid');
    }
}

// Check if channel input is valid
function isValidChannelInput(input) {
    if (!input || input.trim().length === 0) return false;
    
    const patterns = [
        /^https?:\/\/(www\.)?youtube\.com\/@[\w-]+/,  // @username URL
        /^https?:\/\/(www\.)?youtube\.com\/c\/[\w-]+/, // Custom URL
        /^https?:\/\/(www\.)?youtube\.com\/user\/[\w-]+/, // User URL
        /^https?:\/\/(www\.)?youtube\.com\/channel\/UC[\w-]{22}/, // Channel ID URL
        /^@[\w-]+$/, // Direct @username
        /^UC[\w-]{22}$/, // Direct channel ID
        /^[\w-]+$/ // Direct username
    ];
    
    return patterns.some(pattern => pattern.test(input.trim()));
}

// Format channel input
function formatChannelInput(input) {
    input = input.trim();
    
    // If it's just a username without @, add @
    if (input.match(/^[a-zA-Z0-9_-]+$/) && !input.startsWith('@') && !input.startsWith('UC')) {
        return '@' + input;
    }
    
    return input;
}

// Update title metrics in real-time
function updateTitleMetrics(title) {
    const length = title.length;
    const lengthBadge = document.getElementById('titleLength');
    const indicator = document.getElementById('lengthIndicator');
    
    if (lengthBadge) {
        lengthBadge.textContent = length;
        
        // Update badge color based on optimal length
        lengthBadge.className = 'badge ';
        if (length >= 40 && length <= 70) {
            lengthBadge.className += 'bg-success';
            if (indicator) {
                indicator.textContent = 'طول مثالي';
                indicator.className = 'text-success';
            }
        } else if (length >= 30 && length <= 80) {
            lengthBadge.className += 'bg-warning';
            if (indicator) {
                indicator.textContent = length < 40 ? 'قصير نسبياً' : 'طويل نسبياً';
                indicator.className = 'text-warning';
            }
        } else if (length < 30) {
            lengthBadge.className += 'bg-danger';
            if (indicator) {
                indicator.textContent = 'قصير جداً';
                indicator.className = 'text-danger';
            }
        } else {
            lengthBadge.className += 'bg-danger';
            if (indicator) {
                indicator.textContent = 'طويل جداً';
                indicator.className = 'text-danger';
            }
        }
    }
}

// Initialize tooltips
function initializeTooltips() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize animations
function initializeAnimations() {
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in-up');
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.service-card, .feature-card, .step-card');
    animatedElements.forEach(el => observer.observe(el));
}

// Initialize counters
function initializeCounters() {
    const counters = document.querySelectorAll('.stat-counter');
    
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.getAttribute('data-target'));
                const duration = 2000; // 2 seconds
                
                animateCounter(counter, target, duration);
                counterObserver.unobserve(counter);
            }
        });
    });
    
    counters.forEach(counter => counterObserver.observe(counter));
}

// Animate counter
function animateCounter(element, target, duration) {
    const start = 0;
    const startTime = performance.now();
    
    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const current = Math.floor(progress * target);
        element.textContent = formatNumber(current);
        
        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        }
    }
    
    requestAnimationFrame(updateCounter);
}

// Initialize charts placeholder (extended in charts.js)
function initializeCharts() {
    // This will be extended by charts.js
    console.log('Charts initialization - see charts.js for implementation');
}

// Show loading state for forms
function showLoadingState(formId, buttonId) {
    const form = document.getElementById(formId);
    const button = document.getElementById(buttonId);
    
    if (button) {
        button.disabled = true;
        button.classList.add('loading');
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري المعالجة...';
        
        // Store original text for restoration
        button.setAttribute('data-original-text', originalText);
    }
}

// Hide loading state
function hideLoadingState(buttonId) {
    const button = document.getElementById(buttonId);
    
    if (button) {
        button.disabled = false;
        button.classList.remove('loading');
        const originalText = button.getAttribute('data-original-text');
        if (originalText) {
            button.innerHTML = originalText;
        }
    }
}

// Show error message
function showError(message, containerId = 'error-container') {
    let errorDiv = document.getElementById(containerId);
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = containerId;
        errorDiv.className = 'alert alert-danger alert-dismissible fade show mb-4';
        
        // Insert at the top of the main container
        const mainContainer = document.querySelector('.container');
        if (mainContainer) {
            mainContainer.insertBefore(errorDiv, mainContainer.firstChild);
        }
    }
    
    errorDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-exclamation-triangle me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close me-0 ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        if (errorDiv) {
            errorDiv.remove();
        }
    }, 5000);
}

// Show success message
function showSuccess(message, containerId = 'success-container') {
    let successDiv = document.getElementById(containerId);
    
    if (!successDiv) {
        successDiv = document.createElement('div');
        successDiv.id = containerId;
        successDiv.className = 'alert alert-success alert-dismissible fade show mb-4';
        
        // Insert at the top of the main container
        const mainContainer = document.querySelector('.container');
        if (mainContainer) {
            mainContainer.insertBefore(successDiv, mainContainer.firstChild);
        }
    }
    
    successDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-check-circle me-2"></i>
            <span>${message}</span>
            <button type="button" class="btn-close me-0 ms-auto" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        if (successDiv) {
            successDiv.remove();
        }
    }, 3000);
}

// Utility functions
function formatNumber(num) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(1) + 'B';
    }
    if (num >= 1000000) {
        return (num / 1000000).toFixed(1) + 'M';
    }
    if (num >= 1000) {
        return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccess('تم النسخ إلى الحافظة!');
        }).catch(() => {
            showError('فشل في النسخ إلى الحافظة');
        });
    } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        try {
            document.execCommand('copy');
            showSuccess('تم النسخ إلى الحافظة!');
        } catch (err) {
            showError('فشل في النسخ إلى الحافظة');
        }
        document.body.removeChild(textArea);
    }
}

// Export functions for global use
window.fillChannelExample = function(channelName) {
    const input = document.getElementById('channel_input');
    if (input) {
        input.value = channelName;
        input.focus();
        validateChannelInput(channelName);
    }
};

window.fillTitleExample = function(title) {
    const titleInput = document.getElementById('title') || document.getElementById('title_preview');
    if (titleInput) {
        titleInput.value = title;
        titleInput.dispatchEvent(new Event('input'));
        titleInput.focus();
    }
};

// Handle page visibility changes
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // Page is hidden - pause any ongoing animations
        const progressBars = document.querySelectorAll('.progress-bar-animated');
        progressBars.forEach(bar => {
            bar.style.animationPlayState = 'paused';
        });
    } else {
        // Page is visible - resume animations
        const progressBars = document.querySelectorAll('.progress-bar-animated');
        progressBars.forEach(bar => {
            bar.style.animationPlayState = 'running';
        });
    }
});

// Handle form submissions with loading states
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.classList.contains('needs-validation')) {
        if (form.checkValidity()) {
            // Find submit button and show loading state
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                showLoadingState(form.id, submitButton.id);
            }
        }
    }
});

// Progressive enhancement for better UX
if ('serviceWorker' in navigator) {
    // Register service worker for offline functionality (if needed)
    console.log('Service Worker support detected');
}

// Accessibility improvements
document.addEventListener('keydown', function(e) {
    // Escape key to close modals
    if (e.key === 'Escape') {
        const openModals = document.querySelectorAll('.modal.show');
        openModals.forEach(modal => {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        });
    }
});

// Enhanced error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript Error:', e.error);
    // Don't show error to user in production, just log it
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled Promise Rejection:', e.reason);
    // Don't show error to user in production, just log it
});
