/**
 * profile.js - User Profile functionality
 * Handles form validation and submission for user profile and password change
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        ProfilePage.init();
    });
    
    const ProfilePage = {
        elements: {},
        
        init() {
            this.cacheElements();
            this.bindEvents();
        },
        
        cacheElements() {
            this.elements = {
                // Profile form elements
                profileForm: document.querySelector('.profile-form'),
                fnameInput: document.getElementById('fname'),
                lnameInput: document.getElementById('lname'),
                addressInput: document.getElementById('address'),
                cityInput: document.getElementById('city'),
                stateInput: document.getElementById('state'),
                zipInput: document.getElementById('zip'),
                
                // Password form elements
                passwordForm: document.querySelector('.password-form'),
                currentPasswordInput: document.getElementById('current_password'),
                newPasswordInput: document.getElementById('new_password'),
                confirmPasswordInput: document.getElementById('confirm_new_password')
            };
        },
        
        bindEvents() {
            // Profile form submission
            if (this.elements.profileForm) {
                this.elements.profileForm.addEventListener('submit', this.handleProfileFormSubmit.bind(this));
            }
            
            // Password form submission
            if (this.elements.passwordForm) {
                this.elements.passwordForm.addEventListener('submit', this.handlePasswordFormSubmit.bind(this));
            }
            
            // Zip code validation
            if (this.elements.zipInput) {
                this.elements.zipInput.addEventListener('blur', this.validateZipCode.bind(this));
            }
        },
        
        /**
         * Handle profile form submission
         * @param {Event} event - Submit event
         */
        handleProfileFormSubmit(event) {
            // Validate form fields
            const isValid = this.validateProfileForm();
            
            if (!isValid) {
                event.preventDefault();
                return false;
            }
            
            // Form is valid, let it submit normally
            return true;
        },
        
        /**
         * Handle password form submission
         * @param {Event} event - Submit event
         */
        handlePasswordFormSubmit(event) {
            // Validate password fields
            const isValid = this.validatePasswordForm();
            
            if (!isValid) {
                event.preventDefault();
                return false;
            }
            
            // Form is valid, let it submit normally
            return true;
        },
        
        /**
         * Validate profile form fields
         * @returns {boolean} True if valid, false otherwise
         */
        validateProfileForm() {
            let isValid = true;
            
            // First name validation
            if (!this.elements.fnameInput.value.trim()) {
                this.showFieldError(this.elements.fnameInput, 'First name is required');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.fnameInput);
            }
            
            // Last name validation
            if (!this.elements.lnameInput.value.trim()) {
                this.showFieldError(this.elements.lnameInput, 'Last name is required');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.lnameInput);
            }
            
            // Address validation
            if (!this.elements.addressInput.value.trim()) {
                this.showFieldError(this.elements.addressInput, 'Address is required');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.addressInput);
            }
            
            // City validation
            if (!this.elements.cityInput.value.trim()) {
                this.showFieldError(this.elements.cityInput, 'City is required');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.cityInput);
            }
            
            // State validation
            if (!this.elements.stateInput.value.trim()) {
                this.showFieldError(this.elements.stateInput, 'State/Region is required');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.stateInput);
            }
            
            // Zip code validation
            if (!this.validateZipCode()) {
                isValid = false;
            }
            
            return isValid;
        },
        
        /**
         * Validate password form fields
         * @returns {boolean} True if valid, false otherwise
         */
        validatePasswordForm() {
            let isValid = true;
            
            // Current password validation
            if (!this.elements.currentPasswordInput.value) {
                this.showFieldError(this.elements.currentPasswordInput, 'Current password is required');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.currentPasswordInput);
            }
            
            // New password validation
            if (!this.elements.newPasswordInput.value) {
                this.showFieldError(this.elements.newPasswordInput, 'New password is required');
                isValid = false;
            } else if (this.elements.newPasswordInput.value.length < 8) {
                this.showFieldError(this.elements.newPasswordInput, 'Password must be at least 8 characters');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.newPasswordInput);
            }
            
            // Confirm password validation
            if (this.elements.newPasswordInput.value !== this.elements.confirmPasswordInput.value) {
                this.showFieldError(this.elements.confirmPasswordInput, 'Passwords do not match');
                isValid = false;
            } else {
                this.clearFieldError(this.elements.confirmPasswordInput);
            }
            
            return isValid;
        },
        
        /**
         * Validate zip code format
         * @returns {boolean} True if valid, false otherwise
         */
        validateZipCode() {
            const zipValue = this.elements.zipInput.value.trim();
            
            if (!zipValue) {
                this.showFieldError(this.elements.zipInput, 'Postal code is required');
                return false;
            }
            
            // Basic zip code validation (can be customized for different countries)
            const zipRegex = /^\d{5}(-\d{4})?$/;
            
            if (!zipRegex.test(zipValue)) {
                this.showFieldError(this.elements.zipInput, 'Invalid postal code format');
                return false;
            }
            
            this.clearFieldError(this.elements.zipInput);
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
            field.classList.add('profile-input-error');
            
            // Create error message element
            const errorElement = document.createElement('div');
            errorElement.className = 'profile-error-message';
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
            field.classList.remove('profile-input-error');
            
            // Remove any existing error message
            const errorElement = field.parentNode.querySelector('.profile-error-message');
            if (errorElement) {
                errorElement.parentNode.removeChild(errorElement);
            }
        }
    };
})();
