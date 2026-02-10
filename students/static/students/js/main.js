// Main JavaScript for Student Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Form validation enhancement
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Search form enhancement
    var searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            var searchInput = this.querySelector('input[name="q"]');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                window.location.href = window.location.pathname;
            }
        });
    }

    // Dynamic student status update
    var statusBadges = document.querySelectorAll('.status-badge');
    statusBadges.forEach(function(badge) {
        badge.addEventListener('click', function() {
            var studentId = this.dataset.studentId;
            var currentStatus = this.dataset.status;
            var newStatus = prompt('Enter new status (A for Active, I for Inactive, G for Graduated, T for Transferred):', currentStatus);
            
            if (newStatus && 'AIGT'.includes(newStatus.toUpperCase())) {
                updateStudentStatus(studentId, newStatus.toUpperCase());
            }
        });
    });

    // Auto-calculate age from date of birth
    var dobInput = document.getElementById('id_date_of_birth');
    if (dobInput) {
        dobInput.addEventListener('change', function() {
            calculateAge(this.value);
        });
    }

    // File upload preview
    var fileInputs = document.querySelectorAll('input[type="file"][accept="image/*"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            var file = e.target.files[0];
            if (file) {
                previewImage(file, e.target);
            }
        });
    });

    // Table row selection
    var selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            var checkboxes = document.querySelectorAll('.student-checkbox');
            checkboxes.forEach(function(checkbox) {
                checkbox.checked = selectAllCheckbox.checked;
            });
        });
    }

    // Export data functionality
    var exportButtons = document.querySelectorAll('.export-btn');
    exportButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            var format = this.dataset.format || 'csv';
            var type = this.dataset.type || 'students';
            exportData(type, format);
        });
    });

    // Print functionality
    var printButtons = document.querySelectorAll('.print-btn');
    printButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            window.print();
        });
    });

    // Responsive table handling
    window.addEventListener('resize', function() {
        adjustTableResponsiveness();
    });

    // Initialize on page load
    adjustTableResponsiveness();
    initializeCharts();
});

// Helper Functions

function calculateAge(dateString) {
    if (!dateString) return;
    
    var today = new Date();
    var birthDate = new Date(dateString);
    var age = today.getFullYear() - birthDate.getFullYear();
    var m = today.getMonth() - birthDate.getMonth();
    
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }
    
    var ageDisplay = document.getElementById('age-display');
    if (ageDisplay) {
        ageDisplay.textContent = age + ' years';
    }
}

function previewImage(file, inputElement) {
    var reader = new FileReader();
    reader.onload = function(e) {
        var previewContainer = inputElement.parentNode.querySelector('.image-preview');
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'image-preview mt-2';
            inputElement.parentNode.appendChild(previewContainer);
        }
        
        previewContainer.innerHTML = `
            <div class="preview-image-container">
                <img src="${e.target.result}" alt="Preview" class="img-thumbnail" style="max-width: 200px;">
                <button type="button" class="btn btn-sm btn-danger mt-2 remove-preview">
                    <i class="fas fa-times"></i> Remove
                </button>
            </div>
        `;
        
        // Add remove preview functionality
        var removeBtn = previewContainer.querySelector('.remove-preview');
        removeBtn.addEventListener('click', function() {
            inputElement.value = '';
            previewContainer.remove();
        });
    };
    reader.readAsDataURL(file);
}

function updateStudentStatus(studentId, newStatus) {
    // Show loading state
    var badge = document.querySelector(`.status-badge[data-student-id="${studentId}"]`);
    var originalContent = badge.innerHTML;
    badge.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
    
    // Send AJAX request
    fetch(`/api/students/${studentId}/status/`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ status: newStatus })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update badge appearance
            updateBadgeAppearance(badge, newStatus);
            badge.dataset.status = newStatus;
            
            // Show success message
            showToast('Status updated successfully!', 'success');
        } else {
            badge.innerHTML = originalContent;
            showToast('Failed to update status', 'error');
        }
    })
    .catch(error => {
        badge.innerHTML = originalContent;
        showToast('Error updating status', 'error');
        console.error('Error:', error);
    });
}

function updateBadgeAppearance(badge, status) {
    var statusMap = {
        'A': { class: 'bg-success', text: 'Active' },
        'I': { class: 'bg-danger', text: 'Inactive' },
        'G': { class: 'bg-info', text: 'Graduated' },
        'T': { class: 'bg-warning', text: 'Transferred' }
    };
    
    var statusInfo = statusMap[status];
    badge.className = `badge ${statusInfo.class} status-badge`;
    badge.innerHTML = statusInfo.text;
}

function exportData(type, format) {
    // Build export URL
    var url = `/export/${type}/?format=${format}`;
    
    // Add filters if present
    var searchParams = new URLSearchParams(window.location.search);
    searchParams.forEach(function(value, key) {
        url += `&${key}=${encodeURIComponent(value)}`;
    });
    
    // Trigger download
    window.open(url, '_blank');
}

function adjustTableResponsiveness() {
    var tables = document.querySelectorAll('.table-responsive table');
    tables.forEach(function(table) {
        if (table.offsetWidth > table.parentNode.offsetWidth) {
            table.parentNode.classList.add('table-scroll');
        } else {
            table.parentNode.classList.remove('table-scroll');
        }
    });
}

function initializeCharts() {
    // Initialize any charts on the page
    var chartElements = document.querySelectorAll('.chart-container');
    chartElements.forEach(function(element) {
        var chartType = element.dataset.chartType;
        var chartData = JSON.parse(element.dataset.chartData || '{}');
        
        if (chartType && chartData) {
            renderChart(element, chartType, chartData);
        }
    });
}

function renderChart(element, type, data) {
    // Chart.js implementation
    if (typeof Chart !== 'undefined') {
        var ctx = element.getContext('2d');
        new Chart(ctx, {
            type: type,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function showToast(message, type) {
    // Create toast container if it doesn't exist
    var toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 1050;';
        document.body.appendChild(toastContainer);
    }
    
    // Create toast
    var toastId = 'toast-' + Date.now();
    var toast = document.createElement('div');
    toast.id = toastId;
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Initialize and show toast
    var bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + N for new student
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        var newStudentBtn = document.querySelector('a[href*="/students/create/"]');
        if (newStudentBtn) {
            window.location.href = newStudentBtn.href;
        }
    }
    
    // Ctrl/Cmd + F for search focus
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        var searchInput = document.querySelector('input[name="query"], input[type="search"]');
        if (searchInput) {
            searchInput.focus();
        }
    }
    
    // Escape to clear search
    if (e.key === 'Escape') {
        var searchInput = document.querySelector('input[name="query"]');
        if (searchInput && searchInput.value) {
            searchInput.value = '';
            searchInput.form.submit();
        }
    }
});

// Performance monitoring
window.addEventListener('load', function() {
    // Log page load performance
    if (window.performance) {
        var perfData = window.performance.timing;
        var pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log('Page loaded in ' + pageLoadTime + 'ms');
    }
});