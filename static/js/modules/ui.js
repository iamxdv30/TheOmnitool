/**
 * ui.js - UI interaction handlers
 * Provides reusable UI components and interaction handlers
 */

const UIModule = (function() {
    'use strict';
    
    /**
     * Initialize tooltips on the page
     * @param {string} selector - Selector for tooltip elements
     */
    function initTooltips(selector = '[data-bs-toggle="tooltip"]') {
        const tooltipTriggerList = document.querySelectorAll(selector);
        [...tooltipTriggerList].forEach(tooltipTriggerEl => {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    /**
     * Initialize popovers on the page
     * @param {string} selector - Selector for popover elements
     */
    function initPopovers(selector = '[data-bs-toggle="popover"]') {
        const popoverTriggerList = document.querySelectorAll(selector);
        [...popoverTriggerList].forEach(popoverTriggerEl => {
            new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    /**
     * Show a modal dialog
     * @param {string|HTMLElement} modal - Modal selector or element
     * @param {Object} options - Modal options
     */
    function showModal(modal, options = {}) {
        const modalElement = typeof modal === 'string' 
            ? document.querySelector(modal) 
            : modal;
            
        if (!modalElement) return;
        
        const bsModal = new bootstrap.Modal(modalElement, options);
        bsModal.show();
        
        return bsModal;
    }
    
    /**
     * Hide a modal dialog
     * @param {string|HTMLElement} modal - Modal selector or element
     */
    function hideModal(modal) {
        const modalElement = typeof modal === 'string' 
            ? document.querySelector(modal) 
            : modal;
            
        if (!modalElement) return;
        
        const bsModal = bootstrap.Modal.getInstance(modalElement);
        if (bsModal) {
            bsModal.hide();
        }
    }
    
    /**
     * Create a confirmation dialog
     * @param {Object} options - Dialog options
     * @return {Promise} - Resolves with true (confirm) or false (cancel)
     */
    function confirmDialog(options = {}) {
        const defaults = {
            title: 'Confirm Action',
            message: 'Are you sure you want to proceed?',
            confirmText: 'Confirm',
            cancelText: 'Cancel',
            confirmButtonClass: 'btn-primary',
            cancelButtonClass: 'btn-secondary'
        };
        
        const settings = Object.assign({}, defaults, options);
        
        // Create modal element if it doesn't exist
        let modalElement = document.getElementById('uiModuleConfirmModal');
        
        if (!modalElement) {
            modalElement = document.createElement('div');
            modalElement.className = 'modal fade';
            modalElement.id = 'uiModuleConfirmModal';
            modalElement.setAttribute('tabindex', '-1');
            modalElement.setAttribute('aria-hidden', 'true');
            
            modalElement.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title"></h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body"></div>
                        <div class="modal-footer">
                            <button type="button" class="btn cancel-btn" data-bs-dismiss="modal"></button>
                            <button type="button" class="btn confirm-btn"></button>
                        </div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modalElement);
        }
        
        // Update modal content
        modalElement.querySelector('.modal-title').textContent = settings.title;
        modalElement.querySelector('.modal-body').textContent = settings.message;
        
        const cancelBtn = modalElement.querySelector('.cancel-btn');
        cancelBtn.textContent = settings.cancelText;
        cancelBtn.className = `btn ${settings.cancelButtonClass}`;
        
        const confirmBtn = modalElement.querySelector('.confirm-btn');
        confirmBtn.textContent = settings.confirmText;
        confirmBtn.className = `btn ${settings.confirmButtonClass}`;
        
        // Create and return promise
        return new Promise(resolve => {
            const modal = new bootstrap.Modal(modalElement);
            
            // Handle confirm button click
            const handleConfirm = () => {
                confirmBtn.removeEventListener('click', handleConfirm);
                modal.hide();
                resolve(true);
            };
            
            // Handle modal hidden event
            const handleHidden = () => {
                modalElement.removeEventListener('hidden.bs.modal', handleHidden);
                resolve(false);
            };
            
            confirmBtn.addEventListener('click', handleConfirm);
            modalElement.addEventListener('hidden.bs.modal', handleHidden);
            
            modal.show();
        });
    }
    
    /**
     * Show a toast notification
     * @param {Object} options - Toast options
     */
    function showToast(options = {}) {
        const defaults = {
            title: '',
            message: '',
            type: 'info',
            duration: 5000,
            position: 'top-right'
        };
        
        const settings = Object.assign({}, defaults, options);
        
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector(`.toast-container.${settings.position}`);
        
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = `toast-container ${settings.position}`;
            
            // Set position styles
            const positionStyles = {
                'top-right': 'top: 1rem; right: 1rem;',
                'top-left': 'top: 1rem; left: 1rem;',
                'bottom-right': 'bottom: 1rem; right: 1rem;',
                'bottom-left': 'bottom: 1rem; left: 1rem;'
            };
            
            toastContainer.setAttribute('style', `position: fixed; z-index: 1050; ${positionStyles[settings.position]}`);
            document.body.appendChild(toastContainer);
        }
        
        // Create toast element
        const toastElement = document.createElement('div');
        toastElement.className = `toast toast-${settings.type}`;
        toastElement.setAttribute('role', 'alert');
        toastElement.setAttribute('aria-live', 'assertive');
        toastElement.setAttribute('aria-atomic', 'true');
        
        // Set toast content
        toastElement.innerHTML = `
            <div class="toast-header">
                <strong class="me-auto">${settings.title}</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${settings.message}
            </div>
        `;
        
        // Add to container
        toastContainer.appendChild(toastElement);
        
        // Initialize and show toast
        const toast = new bootstrap.Toast(toastElement, {
            autohide: settings.duration > 0,
            delay: settings.duration
        });
        
        toast.show();
        
        // Remove from DOM after hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastContainer.removeChild(toastElement);
            
            // Remove container if empty
            if (toastContainer.children.length === 0) {
                document.body.removeChild(toastContainer);
            }
        });
        
        return toast;
    }
    
    /**
     * Create a loading spinner
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Object} options - Spinner options
     * @return {Object} - Spinner control object
     */
    function createSpinner(container, options = {}) {
        const defaults = {
            size: 'md',
            color: 'primary',
            text: 'Loading...',
            fullscreen: false
        };
        
        const settings = Object.assign({}, defaults, options);
        
        // Create spinner element
        const spinnerElement = document.createElement('div');
        spinnerElement.className = settings.fullscreen ? 'spinner-overlay' : 'spinner-container';
        
        // Set styles
        if (settings.fullscreen) {
            spinnerElement.setAttribute('style', `
                position: fixed;
                top: 0;
                left: 0;
                width: 100vw;
                height: 100vh;
                background-color: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `);
        } else {
            spinnerElement.setAttribute('style', `
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100px;
            `);
        }
        
        // Set spinner content
        spinnerElement.innerHTML = `
            <div class="text-center">
                <div class="spinner-border text-${settings.color} spinner-border-${settings.size}" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                ${settings.text ? `<div class="mt-2">${settings.text}</div>` : ''}
            </div>
        `;
        
        // Add to container if not fullscreen
        if (!settings.fullscreen && container) {
            const containerElement = typeof container === 'string' 
                ? document.querySelector(container) 
                : container;
                
            if (containerElement) {
                containerElement.appendChild(spinnerElement);
            }
        } else if (settings.fullscreen) {
            // Add to body if fullscreen
            document.body.appendChild(spinnerElement);
        }
        
        // Return control object
        return {
            element: spinnerElement,
            show: function() {
                spinnerElement.style.display = 'flex';
            },
            hide: function() {
                spinnerElement.style.display = 'none';
            },
            remove: function() {
                if (spinnerElement.parentNode) {
                    spinnerElement.parentNode.removeChild(spinnerElement);
                }
            },
            setText: function(text) {
                const textElement = spinnerElement.querySelector('.mt-2');
                if (textElement) {
                    textElement.textContent = text;
                }
            }
        };
    }
    
    /**
     * Initialize all UI components
     */
    function initAll() {
        initTooltips();
        initPopovers();
    }
    
    // Public API
    return {
        initTooltips: initTooltips,
        initPopovers: initPopovers,
        showModal: showModal,
        hideModal: hideModal,
        confirmDialog: confirmDialog,
        showToast: showToast,
        createSpinner: createSpinner,
        initAll: initAll
    };
})();
