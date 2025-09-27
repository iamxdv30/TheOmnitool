/**
 * login.js - Enhanced Login functionality
 * Handles form validation, captcha integration, and OAuth (future)
 */

(function() {
    'use strict';
    
    window.LoginPage = {
        elements: {},
        isSubmitting: false,
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.initializeCaptcha();
            this.setupPasswordToggle();
            this.handleRememberMe();
        },
        
        cacheElements() {
            // Form elements
            this.elements.form = document.getElementById('loginForm');
            this.elements.usernameInput = document.getElementById('username');
            this.elements.passwordInput = document.getElementById('password');
            this.elements.rememberMeInput = document.getElementById('remember_me');
            this.elements.submitBtn = document.getElementById('submitBtn');
            this.elements.btnText = this.elements.submitBtn?.querySelector('.btn-text');
            this.elements.btnLoading = this.elements.submitBtn?.querySelector('.btn-loading');
            
            // Password toggle
            this.elements.passwordToggle = document.getElementById('passwordToggle');
            
            // Error elements
            this.elements.usernameError = document.getElementById('usernameError');
            this.elements.passwordError = document.getElementById('passwordError');
            this.elements.captchaError = document.getElementById('captchaError');
            
            // OAuth elements (for future use)
            this.elements.googleLoginBtn = document.getElementById('googleLoginBtn');
            
            // Verification elements
            this.elements.resendForm = document.querySelector('.resend-form');
        },
        
        bindEvents() {
            // Form submission
            if (this.elements.form) {
                this.elements.form.addEventListener('submit', this.handleFormSubmit.bind(this));
            }
            
            // Real-time validation
            if (this.elements.usernameInput) {
                this.elements.usernameInput.addEventListener('blur', () => this.validateUsername());
                this.elements.usernameInput.addEventListener('input', () => this.clearFieldError('username'));
            }
            
            if (this.elements.passwordInput) {
                this.elements.passwordInput.addEventListener('blur', () => this.validatePassword());
                this.elements.passwordInput.addEventListener('input', () => this.clearFieldError('password'));
            }
            
            // Captcha events
            document.addEventListener('captchaSuccess', () => this.clearFieldError('captcha'));
            document.addEventListener('captchaExpired', () => this.showFieldError('captcha', 'Captcha expired. Please verify again.'));
            document.addEventListener('captchaError', () => this.showFieldError('captcha', 'Captcha error. Please try again.'));
            
            // OAuth login (for future implementation)
            if (this.elements.googleLoginBtn) {
                this.elements.googleLoginBtn.addEventListener('click', this.handleGoogleLogin.bind(this));
            }
            
            // Resend verification form
            if (this.elements.resendForm) {
                this.elements.resendForm.addEventListener('submit', this.handleResendVerification.bind(this));
            }
            
            // Keyboard shortcuts
            document.addEventListener('keydown', (event) => {
                // Enter key to submit form
                if (event.key === 'Enter' && this.isFormFocused()) {
                    event.preventDefault();
                    this.handleFormSubmit(event);
                }
            });
        },
        
        async initializeCaptcha() {
            if (typeof window.CaptchaModule !== 'undefined' && window.RECAPTCHA_SITE_KEY) {
                try {
                    await window.CaptchaModule.init();
                    await window.CaptchaModule.render('recaptcha-container');
                } catch (error) {
                    console.error('Failed to initialize captcha:', error);
                    this.showFieldError('captcha', 'Captcha failed to load. Please refresh the page.');
                }
            }
        },
        
        setupPasswordToggle() {
            if (this.elements.passwordToggle) {
                this.elements.passwordToggle.addEventListener('click', () => {
                    const passwordField = this.elements.passwordInput;
                    const isPassword = passwordField.type === 'password';
                    
                    passwordField.type = isPassword ? 'text' : 'password';
                    this.elements.passwordToggle.textContent = isPassword ? '🙈' : '👁️';
                    this.elements.passwordToggle.setAttribute('aria-label', 
                        isPassword ? 'Hide password' : 'Show password');
                });
            }
        },
        
        handleRememberMe() {
            // Load remembered username if available
            if (this.elements.usernameInput && localStorage.getItem('rememberedUsername')) {
                this.elements.usernameInput.value = localStorage.getItem('rememberedUsername');
                if (this.elements.rememberMeInput) {
                    this.elements.rememberMeInput.checked = true;
                }
            }
        },
        
        async handleFormSubmit(event) {
            event.preventDefault();
            
            if (this.isSubmitting) {
                return;
            }
            
            // Validate all fields
            const isValid = this.validateForm();
            
            if (!isValid) {
                return;
            }
            
            // Validate captcha
            if (typeof window.CaptchaModule !== 'undefined') {
                if (!window.CaptchaModule.validateForm(this.elements.form, 'recaptcha-container')) {
                    this.showFieldError('captcha', 'Please complete the captcha verification');
                    return;
                }
            }
            
            this.setSubmittingState(true);
            
            try {
                // Handle remember me
                if (this.elements.rememberMeInput?.checked) {
                    localStorage.setItem('rememberedUsername', this.elements.usernameInput.value);
                } else {
                    localStorage.removeItem('rememberedUsername');
                }
                
                // Submit the form
                this.elements.form.submit();
            } catch (error) {
                console.error('Form submission error:', error);
                this.setSubmittingState(false);
                this.showGeneralError('An error occurred. Please try again.');
            }
        },
        
        validateForm() {
            let isValid = true;
            
            if (!this.validateUsername()) isValid = false;
            if (!this.validatePassword()) isValid = false;
            
            return isValid;
        },
        
        validateUsername() {
            const username = this.elements.usernameInput.value.trim();
            
            if (!username) {
                this.showFieldError('username', 'Username is required');
                return false;
            }
            
            if (username.length < 1 || username.length > 50) {
                this.showFieldError('username', 'Please enter a valid username');
                return false;
            }
            
            this.clearFieldError('username');
            return true;
        },
        
        validatePassword() {
            const password = this.elements.passwordInput.value;
            
            if (!password) {
                this.showFieldError('password', 'Password is required');
                return false;
            }
            
            if (password.length < 1) {
                this.showFieldError('password', 'Please enter your password');
                return false;
            }
            
            this.clearFieldError('password');
            return true;
        },
        
        async handleGoogleLogin() {
            try {
                // This will be implemented when OAuth is added
                console.log('Google login clicked - OAuth not yet implemented');
                this.showGeneralError('Google login will be available in a future update.');
            } catch (error) {
                console.error('Google login error:', error);
                this.showGeneralError('Google login failed. Please try again.');
            }
        },
        
        async handleResendVerification(event) {
            event.preventDefault();
            
            const submitBtn = event.target.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            
            try {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Sending...';
                
                // Submit the resend form
                event.target.submit();
            } catch (error) {
                console.error('Resend verification error:', error);
                this.showGeneralError('Failed to send verification email. Please try again.');
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }
        },
        
        isFormFocused() {
            const activeElement = document.activeElement;
            return this.elements.form?.contains(activeElement) || 
                   activeElement === this.elements.usernameInput || 
                   activeElement === this.elements.passwordInput;
        },
        
        showFieldError(fieldName, message) {
            const errorElement = this.elements[fieldName + 'Error'];
            const inputElement = this.elements[fieldName + 'Input'];
            
            if (errorElement) {
                errorElement.textContent = message;
                errorElement.style.display = 'block';
            }
            
            if (inputElement) {
                inputElement.classList.add('error');
            }
        },
        
        clearFieldError(fieldName) {
            const errorElement = this.elements[fieldName + 'Error'];
            const inputElement = this.elements[fieldName + 'Input'];
            
            if (errorElement) {
                errorElement.textContent = '';
                errorElement.style.display = 'none';
            }
            
            if (inputElement) {
                inputElement.classList.remove('error');
            }
        },
        
        showGeneralError(message) {
            // Show error using existing flash message system
            if (typeof OmniUtils !== 'undefined' && OmniUtils.showFlashMessage) {
                OmniUtils.showFlashMessage(message, 'error');
            } else {
                alert(message); // Fallback
            }
        },
        
        setSubmittingState(isSubmitting) {
            this.isSubmitting = isSubmitting;
            
            if (this.elements.submitBtn) {
                this.elements.submitBtn.disabled = isSubmitting;
            }
            
            if (this.elements.btnText && this.elements.btnLoading) {
                if (isSubmitting) {
                    this.elements.btnText.style.display = 'none';
                    this.elements.btnLoading.style.display = 'inline-flex';
                } else {
                    this.elements.btnText.style.display = 'inline';
                    this.elements.btnLoading.style.display = 'none';
                }
            }
            
            // Disable form inputs during submission
            if (this.elements.usernameInput) {
                this.elements.usernameInput.disabled = isSubmitting;
            }
            if (this.elements.passwordInput) {
                this.elements.passwordInput.disabled = isSubmitting;
            }
        },
        
        // Utility methods for future OAuth integration
        async initializeGoogleAuth() {
            // Placeholder for Google OAuth initialization
            // Will be implemented when OAuth feature is added
            return Promise.resolve();
        },
        
        handleOAuthSuccess(response) {
            // Placeholder for OAuth success handling
            console.log('OAuth success:', response);
        },
        
        handleOAuthError(error) {
            // Placeholder for OAuth error handling
            console.error('OAuth error:', error);
            this.showGeneralError('Authentication failed. Please try again.');
        }
    };

})();