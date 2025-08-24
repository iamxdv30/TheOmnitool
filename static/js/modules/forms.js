/**
 * forms.js - Form handling module
 * Provides reusable form handling functionality
 */

const FormHandler = (function() {
    'use strict';
    
    /**
     * Initialize a form with validation and submission handling
     * @param {string|HTMLElement} formSelector - Form selector or element
     * @param {Object} options - Configuration options
     */
    function initForm(formSelector, options = {}) {
        const form = typeof formSelector === 'string' 
            ? document.querySelector(formSelector) 
            : formSelector;
            
        if (!form) return;
        
        const defaults = {
            validateOnInput: true,
            validateOnBlur: true,
            submitHandler: null,
            validationRules: {},
            errorClass: 'is-invalid',
            errorMessageClass: 'invalid-feedback',
            successClass: 'is-valid',
            showSuccessState: false
        };
        
        const settings = Object.assign({}, defaults, options);
        
        // Bind events
        if (settings.validateOnInput) {
            form.addEventListener('input', handleInput);
        }
        
        if (settings.validateOnBlur) {
            form.addEventListener('blur', handleBlur, true);
        }
        
        form.addEventListener('submit', handleSubmit);
        
        // Store settings on the form element
        form._formHandlerSettings = settings;
        
        /**
         * Handle input events for real-time validation
         * @param {Event} event - Input event
         */
        function handleInput(event) {
            if (event.target.tagName === 'INPUT' || 
                event.target.tagName === 'SELECT' || 
                event.target.tagName === 'TEXTAREA') {
                
                validateField(event.target);
            }
        }
        
        /**
         * Handle blur events for validation
         * @param {Event} event - Blur event
         */
        function handleBlur(event) {
            if (event.target.tagName === 'INPUT' || 
                event.target.tagName === 'SELECT' || 
                event.target.tagName === 'TEXTAREA') {
                
                validateField(event.target);
            }
        }
        
        /**
         * Handle form submission
         * @param {Event} event - Submit event
         */
        function handleSubmit(event) {
            event.preventDefault();
            
            // Validate all fields
            const isValid = validateForm();
            
            if (isValid && typeof settings.submitHandler === 'function') {
                // Get form data
                const formData = new FormData(form);
                const data = {};
                
                for (const [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                // Call submit handler with form data
                settings.submitHandler(data, form);
            }
        }
        
        /**
         * Validate the entire form
         * @return {boolean} - True if form is valid
         */
        function validateForm() {
            const inputs = form.querySelectorAll('input, select, textarea');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!validateField(input)) {
                    isValid = false;
                }
            });
            
            return isValid;
        }
        
        /**
         * Validate a single form field
         * @param {HTMLElement} field - The field to validate
         * @return {boolean} - True if field is valid
         */
        function validateField(field) {
            const name = field.name;
            if (!name || !settings.validationRules[name]) return true;
            
            const rules = settings.validationRules[name];
            const value = field.value;
            let isValid = true;
            let errorMessage = '';
            
            // Check required
            if (rules.required && !value.trim()) {
                isValid = false;
                errorMessage = rules.requiredMessage || 'This field is required';
            }
            
            // Check min length
            else if (rules.minLength && value.length < rules.minLength) {
                isValid = false;
                errorMessage = rules.minLengthMessage || 
                    `Minimum length is ${rules.minLength} characters`;
            }
            
            // Check max length
            else if (rules.maxLength && value.length > rules.maxLength) {
                isValid = false;
                errorMessage = rules.maxLengthMessage || 
                    `Maximum length is ${rules.maxLength} characters`;
            }
            
            // Check pattern
            else if (rules.pattern && !rules.pattern.test(value)) {
                isValid = false;
                errorMessage = rules.patternMessage || 'Invalid format';
            }
            
            // Check custom validator
            else if (rules.validator && typeof rules.validator === 'function') {
                const validatorResult = rules.validator(value, field);
                
                if (validatorResult !== true) {
                    isValid = false;
                    errorMessage = validatorResult || 'Invalid value';
                }
            }
            
            // Update UI based on validation result
            updateFieldState(field, isValid, errorMessage);
            
            return isValid;
        }
        
        /**
         * Update field visual state based on validation
         * @param {HTMLElement} field - The field to update
         * @param {boolean} isValid - Whether the field is valid
         * @param {string} errorMessage - Error message to display
         */
        function updateFieldState(field, isValid, errorMessage) {
            // Remove existing states
            field.classList.remove(settings.errorClass, settings.successClass);
            
            // Remove existing error message
            const parent = field.parentElement;
            const existingError = parent.querySelector(`.${settings.errorMessageClass}`);
            if (existingError) {
                parent.removeChild(existingError);
            }
            
            if (!isValid) {
                // Add error state
                field.classList.add(settings.errorClass);
                
                // Add error message
                const errorElement = document.createElement('div');
                errorElement.className = settings.errorMessageClass;
                errorElement.textContent = errorMessage;
                parent.appendChild(errorElement);
            } else if (settings.showSuccessState) {
                // Add success state if enabled
                field.classList.add(settings.successClass);
            }
        }
        
        // Return public API for this form instance
        return {
            validate: validateForm,
            reset: function() {
                form.reset();
                const inputs = form.querySelectorAll('input, select, textarea');
                inputs.forEach(input => {
                    input.classList.remove(settings.errorClass, settings.successClass);
                    const parent = input.parentElement;
                    const existingError = parent.querySelector(`.${settings.errorMessageClass}`);
                    if (existingError) {
                        parent.removeChild(existingError);
                    }
                });
            },
            getForm: function() {
                return form;
            }
        };
    }
    
    // Common validation rules
    const ValidationRules = {
        email: {
            pattern: /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
            patternMessage: 'Please enter a valid email address'
        },
        password: {
            minLength: 8,
            minLengthMessage: 'Password must be at least 8 characters long',
            pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/,
            patternMessage: 'Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character'
        },
        phone: {
            pattern: /^\+?[0-9]{10,15}$/,
            patternMessage: 'Please enter a valid phone number'
        },
        url: {
            pattern: /^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/,
            patternMessage: 'Please enter a valid URL'
        }
    };
    
    // Public API
    return {
        initForm: initForm,
        ValidationRules: ValidationRules
    };
})();
