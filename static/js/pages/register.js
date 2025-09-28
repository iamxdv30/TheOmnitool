/**
 * register.js - Registration functionality
 * Handles form validation and submission for registration steps
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        RegisterPage.init();
    });
    
    const RegisterPage = {
        elements: {},
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.setupFlashMessages();
        },
        
        cacheElements() {
            // Step 1 form elements
            this.elements.step1Form = document.querySelector('.register-step1-form');
            this.elements.fnameInput = document.querySelector('input[name="fname"]');
            this.elements.lnameInput = document.querySelector('input[name="lname"]');
            this.elements.addressInput = document.querySelector('input[name="address"]');
            this.elements.cityInput = document.querySelector('input[name="city"]');
            this.elements.stateInput = document.querySelector('input[name="state"]');
            this.elements.zipInput = document.querySelector('input[name="zip"]');
            
            // Step 2 form elements
            this.elements.step2Form = document.querySelector('.register-step2-container form');
            this.elements.usernameInput = document.querySelector('#username');
            this.elements.emailInput = document.querySelector('#email');
            this.elements.passwordInput = document.querySelector('#password');
            this.elements.confirmPasswordInput = document.querySelector('#confirm_password');
            
            // Flash messages
            this.elements.flashMessages = document.querySelectorAll('.flash-message');
        },
        
        bindEvents() {
            // Step 1 form submission
            if (this.elements.step1Form) {
                this.elements.step1Form.addEventListener('submit', this.handleStep1FormSubmit.bind(this));
                
                // Input validation events
                if (this.elements.zipInput) {
                    this.elements.zipInput.addEventListener('blur', this.validateZipCode.bind(this));
                }
            }
            
            // Step 2 form submission
            if (this.elements.step2Form) {
                this.elements.step2Form.addEventListener('submit', this.handleStep2FormSubmit.bind(this));
                
                // Input validation events
                if (this.elements.emailInput) {
                    this.elements.emailInput.addEventListener('blur', this.validateEmail.bind(this));
                }
                
                if (this.elements.passwordInput) {
                    this.elements.passwordInput.addEventListener('blur', this.validatePassword.bind(this));
                }
                
                if (this.elements.confirmPasswordInput) {
                    this.elements.confirmPasswordInput.addEventListener('blur', this.validateConfirmPassword.bind(this));
                }
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
         * Handle step 1 form submission
         * @param {Event} event - Submit event
         */
        handleStep1FormSubmit(event) {
            // Validate form fields
            const isValid = this.validateStep1Form();
            
            if (!isValid) {
                event.preventDefault();
                return false;
            }
            
            // Form is valid, let it submit normally
            return true;
        },
        
        /**
         * Handle step 2 form submission
         * @param {Event} event - Submit event
         */
        handleStep2FormSubmit(event) {
            // Validate form fields
            const isValid = this.validateStep2Form();
            
            if (!isValid) {
                event.preventDefault();
                return false;
            }
            
            // Form is valid, let it submit normally
            return true;
        },
        
        /**
         * Validate step 1 form fields
         * @returns {boolean} True if valid, false otherwise
         */
        validateStep1Form() {
            let isValid = true;
            
            // First name validation
            if (this.elements.fnameInput && !this.elements.fnameInput.value.trim()) {
                this.showFieldError(this.elements.fnameInput, 'First name is required');
                isValid = false;
            } else if (this.elements.fnameInput) {
                this.clearFieldError(this.elements.fnameInput);
            }
            
            // Last name validation
            if (this.elements.lnameInput && !this.elements.lnameInput.value.trim()) {
                this.showFieldError(this.elements.lnameInput, 'Last name is required');
                isValid = false;
            } else if (this.elements.lnameInput) {
                this.clearFieldError(this.elements.lnameInput);
            }
            
            // Address validation
            if (this.elements.addressInput && !this.elements.addressInput.value.trim()) {
                this.showFieldError(this.elements.addressInput, 'Address is required');
                isValid = false;
            } else if (this.elements.addressInput) {
                this.clearFieldError(this.elements.addressInput);
            }
            
            // City validation
            if (this.elements.cityInput && !this.elements.cityInput.value.trim()) {
                this.showFieldError(this.elements.cityInput, 'City is required');
                isValid = false;
            } else if (this.elements.cityInput) {
                this.clearFieldError(this.elements.cityInput);
            }
            
            // State validation
            if (this.elements.stateInput && !this.elements.stateInput.value.trim()) {
                this.showFieldError(this.elements.stateInput, 'State is required');
                isValid = false;
            } else if (this.elements.stateInput) {
                this.clearFieldError(this.elements.stateInput);
            }
            
            // Zip code validation
            if (this.elements.zipInput) {
                if (!this.validateZipCode()) {
                    isValid = false;
                }
            }
            
            return isValid;
        },
        
        /**
         * Validate step 2 form fields
         * @returns {boolean} True if valid, false otherwise
         */
        validateStep2Form() {
            let isValid = true;
            
            // Username validation
            if (this.elements.usernameInput && !this.elements.usernameInput.value.trim()) {
                this.showFieldError(this.elements.usernameInput, 'Username is required');
                isValid = false;
            } else if (this.elements.usernameInput) {
                this.clearFieldError(this.elements.usernameInput);
            }
            
            // Email validation
            if (this.elements.emailInput) {
                if (!this.validateEmail()) {
                    isValid = false;
                }
            }
            
            // Password validation
            if (this.elements.passwordInput) {
                if (!this.validatePassword()) {
                    isValid = false;
                }
            }
            
            // Confirm password validation
            if (this.elements.confirmPasswordInput) {
                if (!this.validateConfirmPassword()) {
                    isValid = false;
                }
            }
            
            return isValid;
        },
        
        /**
         * Validate zip code format
         * @returns {boolean} True if valid, false otherwise
         */
        validateZipCode() {
            if (!this.elements.zipInput) return true;
            
            const zipValue = this.elements.zipInput.value.trim();
            
            if (!zipValue) {
                this.showFieldError(this.elements.zipInput, 'ZIP code is required');
                return false;
            }
            
            // Basic zip code validation (can be customized for different countries)
            const zipRegex = /^\d{5}(-\d{4})?$/;
            
            if (!zipRegex.test(zipValue)) {
                this.showFieldError(this.elements.zipInput, 'Invalid ZIP code format');
                return false;
            }
            
            this.clearFieldError(this.elements.zipInput);
            return true;
        },
        
        /**
         * Validate email format
         * @returns {boolean} True if valid, false otherwise
         */
        validateEmail() {
            if (!this.elements.emailInput) return true;
            
            const emailValue = this.elements.emailInput.value.trim();
            
            if (!emailValue) {
                this.showFieldError(this.elements.emailInput, 'Email is required');
                return false;
            }
            
            // Basic email validation
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            
            if (!emailRegex.test(emailValue)) {
                this.showFieldError(this.elements.emailInput, 'Invalid email format');
                return false;
            }
            
            this.clearFieldError(this.elements.emailInput);
            return true;
        },
        
        /**
         * Validate password strength
         * @returns {boolean} True if valid, false otherwise
         */
        validatePassword() {
            if (!this.elements.passwordInput) return true;
            
            const passwordValue = this.elements.passwordInput.value;
            
            if (!passwordValue) {
                this.showFieldError(this.elements.passwordInput, 'Password is required');
                return false;
            }
            
            if (passwordValue.length < 8) {
                this.showFieldError(this.elements.passwordInput, 'Password must be at least 8 characters');
                return false;
            }
            
            this.clearFieldError(this.elements.passwordInput);
            return true;
        },
        
        /**
         * Validate confirm password matches password
         * @returns {boolean} True if valid, false otherwise
         */
        validateConfirmPassword() {
            if (!this.elements.confirmPasswordInput || !this.elements.passwordInput) return true;
            
            const confirmValue = this.elements.confirmPasswordInput.value;
            const passwordValue = this.elements.passwordInput.value;
            
            if (!confirmValue) {
                this.showFieldError(this.elements.confirmPasswordInput, 'Confirm password is required');
                return false;
            }
            
            if (confirmValue !== passwordValue) {
                this.showFieldError(this.elements.confirmPasswordInput, 'Passwords do not match');
                return false;
            }
            
            this.clearFieldError(this.elements.confirmPasswordInput);
            return true;
        },
        
        /**
         * Show error message for a field
         * @param {HTMLElement} field - Form field
         * @param {string} message - Error message
         */
        showFieldError(field, message) {
            // Clear any existing error
            this.clearFieldError(field);
            
            // Add error class to input
            field.classList.add('register-input-error');
            
            // Create error message element
            const errorElement = document.createElement('div');
            errorElement.className = 'register-error-message';
            errorElement.textContent = message;
            
            // Insert error message after the input
            field.parentNode.insertBefore(errorElement, field.nextSibling);
        },
        
        /**
         * Clear error message for a field
         * @param {HTMLElement} field - Form field
         */
        clearFieldError(field) {
            // Remove error class from input
            field.classList.remove('register-input-error');
            
            // Remove any existing error message
            const errorElement = field.parentNode.querySelector('.register-error-message');
            if (errorElement) {
                errorElement.parentNode.removeChild(errorElement);
            }
        }
    };
})();
