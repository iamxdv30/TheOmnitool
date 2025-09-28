/**
 * login.js - Login page functionality
 * Handles form validation and submission for login
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        LoginPage.init();
    });
    
    const LoginPage = {
        elements: {},
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.setupFlashMessages();
        },
        
        cacheElements() {
            this.elements = {
                // Login form elements
                loginForm: document.querySelector('.login-container form'),
                usernameInput: document.querySelector('input[name="username"]'),
                passwordInput: document.querySelector('input[name="password"]'),
                submitButton: document.querySelector('.login-container button[type="submit"]'),
                
                // Flash messages
                flashMessages: document.querySelectorAll('.flash-message')
            };
        },
        
        bindEvents() {
            // Login form submission
            if (this.elements.loginForm) {
                this.elements.loginForm.addEventListener('submit', this.handleLoginFormSubmit.bind(this));
            }
            
            // Input validation
            if (this.elements.usernameInput) {
                this.elements.usernameInput.addEventListener('blur', this.validateUsername.bind(this));
            }
            
            if (this.elements.passwordInput) {
                this.elements.passwordInput.addEventListener('blur', this.validatePassword.bind(this));
            }
        },
        
        /**
         * Set up auto-hiding flash messages
         */
        setupFlashMessages() {
            if (this.elements.flashMessages.length > 0) {
                this.elements.flashMessages.forEach(message => {
                    // Auto-hide flash messages after 5 seconds
                    setTimeout(() => {
                        message.style.opacity = '0';
                        setTimeout(() => {
                            message.style.display = 'none';
                        }, 500); // Wait for fade out animation
                    }, 5000);
                });
            }
        },
        
        /**
         * Handle login form submission
         * @param {Event} event - Submit event
         */
        handleLoginFormSubmit(event) {
            // Validate form fields
            const isUsernameValid = this.validateUsername();
            const isPasswordValid = this.validatePassword();
            
            if (!isUsernameValid || !isPasswordValid) {
                event.preventDefault();
                return false;
            }
            
            // Form is valid, let it submit normally
            return true;
        },
        
        /**
         * Validate username field
         * @returns {boolean} True if valid, false otherwise
         */
        validateUsername() {
            const username = this.elements.usernameInput.value.trim();
            
            if (!username) {
                this.showFieldError(this.elements.usernameInput, 'Username is required');
                return false;
            }
            
            // Additional validation rules can be added here
            
            this.clearFieldError(this.elements.usernameInput);
            return true;
        },
        
        /**
         * Validate password field
         * @returns {boolean} True if valid, false otherwise
         */
        validatePassword() {
            const password = this.elements.passwordInput.value;
            
            if (!password) {
                this.showFieldError(this.elements.passwordInput, 'Password is required');
                return false;
            }
            
            // Additional validation rules can be added here
            
            this.clearFieldError(this.elements.passwordInput);
            return true;
        },
        
        /**
         * Show error message for a field
         * @param {HTMLElement} field - Form field
         * @param {string} message - Error message
         */
        showFieldError(field, message) {
            // Get the error element that's already in the HTML
            const errorElement = document.getElementById(`${field.id}-error`);
            
            if (errorElement) {
                // Set error message and show it
                errorElement.textContent = message;
                errorElement.style.display = 'block';
            }
            
            // Add error class to field
            field.classList.add('error');
            
            // Add ARIA attributes for accessibility
            field.setAttribute('aria-invalid', 'true');
            if (errorElement) {
                field.setAttribute('aria-describedby', field.id + '-error');
            }
        },
        
        /**
         * Clear error message for a field
         * @param {HTMLElement} field - Form field
         */
        clearFieldError(field) {
            const errorElement = document.getElementById(`${field.id}-error`);
            
            if (errorElement) {
                errorElement.style.display = 'none';
            }
            
            // Remove error class and ARIA attributes
            field.classList.remove('error');
            field.removeAttribute('aria-invalid');
            field.removeAttribute('aria-describedby');
        }
    };
})();
