/**
 * register.js - Enhanced Registration functionality
 * Handles form validation, password strength, and captcha integration
 */

(function() {
    'use strict';
    
    window.RegisterPage = {
        elements: {},
        isSubmitting: false,
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.initializeCaptcha();
            this.setupPasswordToggle();
            this.setupPasswordStrength();
        },
        
        cacheElements() {
            // Form elements
            this.elements.form = document.getElementById('registrationForm');
            this.elements.nameInput = document.getElementById('name');
            this.elements.usernameInput = document.getElementById('username');
            this.elements.emailInput = document.getElementById('email');
            this.elements.passwordInput = document.getElementById('password');
            this.elements.confirmPasswordInput = document.getElementById('confirm_password');
            this.elements.submitBtn = document.getElementById('submitBtn');
            this.elements.btnText = this.elements.submitBtn?.querySelector('.btn-text');
            this.elements.btnLoading = this.elements.submitBtn?.querySelector('.btn-loading');
            
            // Password toggle
            this.elements.passwordToggle = document.getElementById('passwordToggle');
            
            // Password strength elements
            this.elements.strengthFill = document.getElementById('strengthFill');
            this.elements.strengthText = document.getElementById('strengthText');
            
            // Error elements
            this.elements.nameError = document.getElementById('nameError');
            this.elements.usernameError = document.getElementById('usernameError');
            this.elements.emailError = document.getElementById('emailError');
            this.elements.passwordError = document.getElementById('passwordError');
            this.elements.confirmPasswordError = document.getElementById('confirmPasswordError');
            this.elements.captchaError = document.getElementById('captchaError');
        },
        
        bindEvents() {
            // Form submission
            if (this.elements.form) {
                this.elements.form.addEventListener('submit', this.handleFormSubmit.bind(this));
            }
            
            // Real-time validation
            if (this.elements.nameInput) {
                this.elements.nameInput.addEventListener('blur', () => this.validateName());
                this.elements.nameInput.addEventListener('input', () => this.clearFieldError('name'));
            }
            
            if (this.elements.usernameInput) {
                this.elements.usernameInput.addEventListener('blur', () => this.validateUsername());
                this.elements.usernameInput.addEventListener('input', () => this.clearFieldError('username'));
            }
            
            if (this.elements.emailInput) {
                this.elements.emailInput.addEventListener('blur', () => this.validateEmail());
                this.elements.emailInput.addEventListener('input', () => this.clearFieldError('email'));
            }
            
            if (this.elements.passwordInput) {
                this.elements.passwordInput.addEventListener('input', () => {
                    this.updatePasswordStrength();
                    this.clearFieldError('password');
                    if (this.elements.confirmPasswordInput.value) {
                        this.validatePasswordConfirmation();
                    }
                });
                this.elements.passwordInput.addEventListener('blur', () => this.validatePassword());
            }
            
            if (this.elements.confirmPasswordInput) {
                this.elements.confirmPasswordInput.addEventListener('blur', () => this.validatePasswordConfirmation());
                this.elements.confirmPasswordInput.addEventListener('input', () => this.clearFieldError('confirmPassword'));
            }
            
            // Captcha events
            document.addEventListener('captchaSuccess', () => this.clearFieldError('captcha'));
            document.addEventListener('captchaExpired', () => this.showFieldError('captcha', 'Captcha expired. Please verify again.'));
            document.addEventListener('captchaError', () => this.showFieldError('captcha', 'Captcha error. Please try again.'));
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
        
        setupPasswordStrength() {
            if (this.elements.passwordInput) {
                this.updatePasswordStrength();
            }
        },
        
        updatePasswordStrength() {
            const password = this.elements.passwordInput.value;
            const strength = this.calculatePasswordStrength(password);
            
            // Update strength bar
            if (this.elements.strengthFill && this.elements.strengthText) {
                this.elements.strengthFill.style.width = `${strength.score * 20}%`;
                this.elements.strengthFill.className = `strength-fill strength-${strength.level}`;
                this.elements.strengthText.textContent = strength.text;
            }
        },
        
        calculatePasswordStrength(password) {
            if (!password) {
                return { score: 0, level: 'none', text: 'Password strength' };
            }
            
            let score = 0;
            const checks = {
                length: password.length >= 8,
                lowercase: /[a-z]/.test(password),
                uppercase: /[A-Z]/.test(password),
                numbers: /\d/.test(password),
                special: /[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)
            };
            
            // Score calculation
            if (checks.length) score += 1;
            if (checks.lowercase) score += 1;
            if (checks.uppercase) score += 1;
            if (checks.numbers) score += 1;
            if (checks.special) score += 1;
            
            // Length bonus
            if (password.length >= 12) score += 0.5;
            if (password.length >= 16) score += 0.5;
            
            // Determine strength level
            let level, text;
            if (score < 2) {
                level = 'weak';
                text = 'Weak password';
            } else if (score < 3) {
                level = 'fair';
                text = 'Fair password';
            } else if (score < 4) {
                level = 'good';
                text = 'Good password';
            } else if (score < 5) {
                level = 'strong';
                text = 'Strong password';
            } else {
                level = 'excellent';
                text = 'Excellent password';
            }
            
            return { score: Math.min(score, 5), level, text };
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
                // Submit the form
                this.elements.form.submit();
            } catch (error) {
                console.error('Form submission error:', error);
                this.setSubmittingState(false);
                OmniUtils.showFlashMessage('An error occurred. Please try again.', 'error');
            }
        },
        
        validateForm() {
            let isValid = true;
            
            if (!this.validateName()) isValid = false;
            if (!this.validateUsername()) isValid = false;
            if (!this.validateEmail()) isValid = false;
            if (!this.validatePassword()) isValid = false;
            if (!this.validatePasswordConfirmation()) isValid = false;
            
            return isValid;
        },
        
        validateName() {
            const name = this.elements.nameInput.value.trim();
            
            if (!name) {
                this.showFieldError('name', 'Name is required');
                return false;
            }
            
            if (name.length < 2) {
                this.showFieldError('name', 'Name must be at least 2 characters');
                return false;
            }
            
            if (name.length > 100) {
                this.showFieldError('name', 'Name must be less than 100 characters');
                return false;
            }
            
            if (!/^[a-zA-Z\s\'-]+$/.test(name)) {
                this.showFieldError('name', 'Name can only contain letters, spaces, hyphens, and apostrophes');
                return false;
            }
            
            this.clearFieldError('name');
            return true;
        },
        
        validateUsername() {
            const username = this.elements.usernameInput.value.trim();
            
            if (!username) {
                this.showFieldError('username', 'Username is required');
                return false;
            }
            
            if (username.length < 3) {
                this.showFieldError('username', 'Username must be at least 3 characters');
                return false;
            }
            
            if (username.length > 50) {
                this.showFieldError('username', 'Username must be less than 50 characters');
                return false;
            }
            
            if (!/^[a-zA-Z0-9_]+$/.test(username)) {
                this.showFieldError('username', 'Username can only contain letters, numbers, and underscores');
                return false;
            }
            
            this.clearFieldError('username');
            return true;
        },
        
        validateEmail() {
            const email = this.elements.emailInput.value.trim();
            
            if (!email) {
                this.showFieldError('email', 'Email is required');
                return false;
            }
            
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                this.showFieldError('email', 'Please enter a valid email address');
                return false;
            }
            
            if (email.length > 255) {
                this.showFieldError('email', 'Email address is too long');
                return false;
            }
            
            this.clearFieldError('email');
            return true;
        },
        
        validatePassword() {
            const password = this.elements.passwordInput.value;
            
            if (!password) {
                this.showFieldError('password', 'Password is required');
                return false;
            }
            
            // Check minimum length
            if (password.length < 8) {
                this.showFieldError('password', 'Password must be at least 8 characters long');
                return false;
            }
            
            // Check requirements
            const requirements = [];
            if (!/[A-Z]/.test(password)) requirements.push('uppercase letter');
            if (!/[a-z]/.test(password)) requirements.push('lowercase letter');
            if (!/\d/.test(password)) requirements.push('number');
            if (!/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) requirements.push('special character');
            
            if (requirements.length > 0) {
                this.showFieldError('password', `Password must contain at least 1 ${requirements.join(', 1 ')}`);
                return false;
            }
            
            this.clearFieldError('password');
            return true;
        },
        
        validatePasswordConfirmation() {
            const password = this.elements.passwordInput.value;
            const confirmPassword = this.elements.confirmPasswordInput.value;
            
            if (!confirmPassword) {
                this.showFieldError('confirmPassword', 'Password confirmation is required');
                return false;
            }
            
            if (password !== confirmPassword) {
                this.showFieldError('confirmPassword', 'Passwords do not match');
                return false;
            }
            
            this.clearFieldError('confirmPassword');
            return true;
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
        }
    };

})();