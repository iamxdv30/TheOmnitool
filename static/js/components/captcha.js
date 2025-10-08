/**
 * Captcha Component for OmniTools
 * Handles Google reCAPTCHA v2 integration with fallback handling
 */

(function() {
    'use strict';

    // Global captcha management
    window.CaptchaModule = {
        isLoaded: false,
        callbacks: [],
        widgets: new Map(),
        
        /**
         * Initialize captcha system
         */
        init() {
            if (this.isLoaded) {
                return Promise.resolve();
            }

            return new Promise((resolve, reject) => {
                // Check if reCAPTCHA is available
                if (typeof grecaptcha !== 'undefined') {
                    this.isLoaded = true;
                    this.processCallbacks();
                    resolve();
                    return;
                }

                // Add callback for when reCAPTCHA loads
                this.callbacks.push(() => {
                    this.isLoaded = true;
                    resolve();
                });

                // Set timeout for loading failure
                setTimeout(() => {
                    if (!this.isLoaded) {
                        console.warn('reCAPTCHA failed to load within timeout');
                        reject(new Error('reCAPTCHA loading timeout'));
                    }
                }, 10000);
            });
        },

        /**
         * Process queued callbacks when reCAPTCHA loads
         */
        processCallbacks() {
            this.callbacks.forEach(callback => {
                try {
                    callback();
                } catch (error) {
                    console.error('Captcha callback error:', error);
                }
            });
            this.callbacks = [];
        },

        /**
         * Render captcha widget
         * @param {string} containerId - ID of container element
         * @param {Object} options - reCAPTCHA options
         * @returns {Promise<string>} Widget ID
         */
        render(containerId, options = {}) {
            return new Promise((resolve, reject) => {
                const renderWidget = () => {
                    try {
                        const container = document.getElementById(containerId);
                        if (!container) {
                            reject(new Error(`Container ${containerId} not found`));
                            return;
                        }

                        // Default options
                        const defaultOptions = {
                            sitekey: window.RECAPTCHA_SITE_KEY,
                            theme: 'light',
                            size: 'normal',
                            callback: (response) => this.onSuccess(containerId, response),
                            'expired-callback': () => this.onExpired(containerId),
                            'error-callback': () => this.onError(containerId)
                        };

                        const widgetOptions = { ...defaultOptions, ...options };

                        // Render the widget
                        const widgetId = grecaptcha.render(container, widgetOptions);
                        
                        // Store widget reference
                        this.widgets.set(containerId, {
                            widgetId: widgetId,
                            container: container,
                            isVerified: false
                        });

                        resolve(widgetId);
                    } catch (error) {
                        console.error('Failed to render captcha:', error);
                        reject(error);
                    }
                };

                if (this.isLoaded) {
                    renderWidget();
                } else {
                    this.callbacks.push(renderWidget);
                }
            });
        },

        /**
         * Reset captcha widget
         * @param {string} containerId - Container ID
         */
        reset(containerId) {
            const widget = this.widgets.get(containerId);
            if (widget && this.isLoaded) {
                try {
                    grecaptcha.reset(widget.widgetId);
                    widget.isVerified = false;
                    this.updateUI(containerId, false);
                } catch (error) {
                    console.error('Failed to reset captcha:', error);
                }
            }
        },

        /**
         * Get response token
         * @param {string} containerId - Container ID
         * @returns {string} Response token
         */
        getResponse(containerId) {
            const widget = this.widgets.get(containerId);
            if (widget && this.isLoaded) {
                try {
                    return grecaptcha.getResponse(widget.widgetId);
                } catch (error) {
                    console.error('Failed to get captcha response:', error);
                    return '';
                }
            }
            return '';
        },

        /**
         * Check if captcha is verified
         * @param {string} containerId - Container ID
         * @returns {boolean} Verification status
         */
        isVerified(containerId) {
            const widget = this.widgets.get(containerId);
            return widget ? widget.isVerified : false;
        },

        /**
         * Handle successful verification
         * @param {string} containerId - Container ID
         * @param {string} response - Response token
         */
        onSuccess(containerId, response) {
            const widget = this.widgets.get(containerId);
            if (widget) {
                widget.isVerified = true;
                this.updateUI(containerId, true);
                
                // Trigger custom event
                const event = new CustomEvent('captchaSuccess', {
                    detail: { containerId, response }
                });
                document.dispatchEvent(event);
            }
        },

        /**
         * Handle captcha expiration
         * @param {string} containerId - Container ID
         */
        onExpired(containerId) {
            const widget = this.widgets.get(containerId);
            if (widget) {
                widget.isVerified = false;
                this.updateUI(containerId, false);
                
                // Trigger custom event
                const event = new CustomEvent('captchaExpired', {
                    detail: { containerId }
                });
                document.dispatchEvent(event);
            }
        },

        /**
         * Handle captcha error
         * @param {string} containerId - Container ID
         */
        onError(containerId) {
            const widget = this.widgets.get(containerId);
            if (widget) {
                widget.isVerified = false;
                this.updateUI(containerId, false);
                
                // Trigger custom event
                const event = new CustomEvent('captchaError', {
                    detail: { containerId }
                });
                document.dispatchEvent(event);
            }
        },

        /**
         * Update UI based on verification status
         * @param {string} containerId - Container ID
         * @param {boolean} isVerified - Verification status
         */
        updateUI(containerId, isVerified) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const parent = container.closest('.captcha-wrapper') || container.parentElement;
            
            if (isVerified) {
                parent.classList.add('captcha-verified');
                parent.classList.remove('captcha-error');
            } else {
                parent.classList.remove('captcha-verified');
            }
        },

        /**
         * Validate form captcha before submission
         * @param {HTMLFormElement} form - Form element
         * @param {string} containerId - Captcha container ID
         * @returns {boolean} Validation result
         */
        validateForm(form, containerId) {
            if (!this.isLoaded) {
                console.warn('reCAPTCHA not loaded');
                return false;
            }

            const response = this.getResponse(containerId);
            if (!response) {
                this.showError(containerId, 'Please complete the captcha verification');
                return false;
            }

            this.clearError(containerId);
            return true;
        },

        /**
         * Show captcha error
         * @param {string} containerId - Container ID
         * @param {string} message - Error message
         */
        showError(containerId, message) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const parent = container.closest('.captcha-wrapper') || container.parentElement;
            parent.classList.add('captcha-error');

            // Remove existing error message
            const existingError = parent.querySelector('.captcha-error-message');
            if (existingError) {
                existingError.remove();
            }

            // Add new error message
            const errorElement = document.createElement('div');
            errorElement.className = 'captcha-error-message';
            errorElement.textContent = message;
            parent.appendChild(errorElement);
        },

        /**
         * Clear captcha error
         * @param {string} containerId - Container ID
         */
        clearError(containerId) {
            const container = document.getElementById(containerId);
            if (!container) return;

            const parent = container.closest('.captcha-wrapper') || container.parentElement;
            parent.classList.remove('captcha-error');

            const errorElement = parent.querySelector('.captcha-error-message');
            if (errorElement) {
                errorElement.remove();
            }
        }
    };

    // Global callback for reCAPTCHA API
    window.onRecaptchaLoad = function() {
        window.CaptchaModule.processCallbacks();
    };

    // Auto-initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        // Add captcha CSS styles
        const style = document.createElement('style');
        style.textContent = `
            .captcha-wrapper {
                margin: 1rem 0;
                position: relative;
            }
            
            .captcha-wrapper.captcha-verified .g-recaptcha {
                border: 2px solid #28a745;
                border-radius: 4px;
            }
            
            .captcha-wrapper.captcha-error .g-recaptcha {
                border: 2px solid #dc3545;
                border-radius: 4px;
            }
            
            .captcha-error-message {
                color: #dc3545;
                font-size: 0.875rem;
                margin-top: 0.25rem;
                display: block;
            }
            
            .captcha-loading {
                display: flex;
                align-items: center;
                justify-content: center;
                height: 78px;
                background-color: #f5f5f5;
                border: 1px solid #ddd;
                border-radius: 4px;
                color: #666;
            }
        `;
        document.head.appendChild(style);

        // Initialize captcha for any existing containers
        const captchaContainers = document.querySelectorAll('[data-captcha]');
        captchaContainers.forEach(container => {
            const containerId = container.id;
            if (containerId) {
                window.CaptchaModule.render(containerId).catch(error => {
                    console.error(`Failed to initialize captcha for ${containerId}:`, error);
                });
            }
        });
    });

})();