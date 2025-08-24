/**
 * contact.js - Contact page functionality
 * Handles contact form submission and email verification
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        ContactPage.init();
    });
    
    // Handle visibility change (tab/window hidden)
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            ContactPage.checkVerificationStatus();
        }
    });
    
    const ContactPage = {
        elements: {},
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.checkVerificationStatus();
            this.loadStoredUserData();
        },
        
        cacheElements() {
            this.elements = {
                verifyEmailBtn: document.getElementById('verifyEmailBtn'),
                messageContainer: document.getElementById('messageContainer'),
                contactForm: document.getElementById('contactForm'),
                emailInput: document.getElementById('email'),
                nameInput: document.getElementById('name'),
                messageInput: document.getElementById('message'),
                queryTypeSelect: document.getElementById('query_type'),
                submitBtn: document.querySelector('.contact-btn')
            };
            
            // Initially hide message area and submit button if verification is required
            if (this.elements.messageContainer && this.elements.submitBtn) {
                this.elements.messageContainer.style.display = 'none';
                this.elements.submitBtn.style.display = 'none';
            }
        },
        
        bindEvents() {
            if (this.elements.verifyEmailBtn) {
                this.elements.verifyEmailBtn.addEventListener('click', this.handleEmailVerification.bind(this));
            }
            
            if (this.elements.contactForm) {
                this.elements.contactForm.addEventListener('submit', this.handleFormSubmit.bind(this));
            }
            
            if (this.elements.emailInput) {
                this.elements.emailInput.addEventListener('blur', this.validateEmail.bind(this));
            }
        },
        
        /**
         * Handle email verification button click
         * @param {Event} event - Click event
         */
        handleEmailVerification(event) {
            event.preventDefault();
            
            const email = this.elements.emailInput.value.trim();
            const name = this.elements.nameInput.value.trim();
            
            if (!name) {
                alert('Please enter your name.');
                return;
            }
            
            if (!EmailUtils.isValidEmail(email)) {
                alert('Please enter a valid email address.');
                return;
            }
            
            // Show loading state
            this.elements.verifyEmailBtn.disabled = true;
            
            // Send verification email using fetch to match original implementation
            fetch('/contact/verify-email', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email, name })
            })
            .then(response => {
                // Check if the response is ok (status in the range 200-299)
                if (response.ok) {
                    return response.json().then(result => {
                        alert('Please check your email for the verification link.');
                        this.elements.verifyEmailBtn.disabled = true;
                        this.elements.emailInput.readOnly = true;
                        this.elements.nameInput.readOnly = true;
                    });
                } else {
                    // If the response is not ok, parse the JSON to get the error message
                    return response.json().then(result => {
                        // Throw an error to be caught by the .catch block
                        throw new Error(result.message || 'Verification failed. Please try again.');
                    });
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error verifying email. Please try again later.');
                this.elements.verifyEmailBtn.disabled = false;
            });
        },
        
        /**
         * Check email verification status
         */
        checkVerificationStatus() {
            // Use fetch API directly to match original implementation
            fetch('/contact/check-verification-status')
                .then(response => response.json())
                .then(data => {
                    if (data.verified) {
                        if (this.elements.emailInput) {
                            this.elements.emailInput.value = data.email;
                            this.elements.emailInput.readOnly = true;
                        }
                        this.showMessageElements();
                    } else {
                        this.hideMessageElements();
                    }
                })
                .catch(error => {
                    console.error('Error checking verification status:', error);
                    this.hideMessageElements();
                });
        },
        
        /**
         * Show message elements after verification
         */
        showMessageElements() {
            if (this.elements.messageContainer) {
                this.elements.messageContainer.style.display = 'block';
            }
            if (this.elements.submitBtn) {
                this.elements.submitBtn.style.display = 'block';
            }
            if (this.elements.verifyEmailBtn) {
                this.elements.verifyEmailBtn.disabled = true;
            }
            if (this.elements.emailInput) {
                this.elements.emailInput.readOnly = true;
            }
            if (this.elements.nameInput) {
                this.elements.nameInput.readOnly = true;
            }
        },
        
        /**
         * Hide message elements when not verified
         */
        hideMessageElements() {
            if (this.elements.messageContainer) {
                this.elements.messageContainer.style.display = 'none';
            }
            if (this.elements.submitBtn) {
                this.elements.submitBtn.style.display = 'none';
            }
            if (this.elements.verifyEmailBtn) {
                this.elements.verifyEmailBtn.disabled = false;
            }
            if (this.elements.emailInput) {
                this.elements.emailInput.readOnly = false;
            }
            if (this.elements.nameInput) {
                this.elements.nameInput.readOnly = false;
            }
        },
        
        /**
         * Reset the form
         */
        resetForm() {
            if (this.elements.contactForm) {
                this.elements.contactForm.reset();
            }
            if (this.elements.verifyEmailBtn) {
                this.elements.verifyEmailBtn.disabled = false;
            }
            if (this.elements.emailInput) {
                this.elements.emailInput.readOnly = false;
            }
            if (this.elements.nameInput) {
                this.elements.nameInput.readOnly = false;
            }
        },
        
        /**
         * Validate email field
         */
        validateEmail() {
            const email = this.elements.emailInput.value;
            
            if (!email) return;
            
            // Use EmailUtils for validation
            return EmailUtils.isValidEmail(email);
        },
        
        /**
         * Handle contact form submission
         * @param {Event} event - Submit event
         */
        handleFormSubmit(event) {
            event.preventDefault();
            
            // Verify email status before submitting
            fetch('/contact/check-verification-status')
                .then(response => response.json())
                .then(verificationData => {
                    if (!verificationData.verified) {
                        alert('Please verify your email before submitting a message.');
                        this.hideMessageElements();
                        return;
                    }
                    
                    const formData = new FormData(this.elements.contactForm);
                    const jsonData = Object.fromEntries(formData.entries());
                    
                    // Show loading state
                    if (this.elements.submitBtn) {
                        this.elements.submitBtn.disabled = true;
                    }
                    
                    fetch('/contact', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(jsonData),
                    })
                    .then(response => {
                        if (response.ok) {
                            return response.json().then(result => {
                                alert('Message sent successfully!');
                                this.resetForm();
                                this.hideMessageElements();
                                // Clear session after successful submission
                                fetch('/clear-session', { method: 'POST' });
                            });
                        } else {
                            return response.json().then(result => {
                                throw new Error(result.message || 'Error sending message.');
                            });
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert(error.message || 'Error sending message. Please try again later.');
                        this.hideMessageElements();
                    })
                    .finally(() => {
                        // Reset button state
                        if (this.elements.submitBtn) {
                            this.elements.submitBtn.disabled = false;
                        }
                    });
                })
                .catch(error => {
                    console.error('Error checking verification status:', error);
                    alert('Error verifying your email status. Please try again.');
                });
        },
        
        /**
         * Load stored user data from session storage
         */
        loadStoredUserData() {
            // Check for stored verification data
            const verifiedName = sessionStorage.getItem('verified_user_name');
            const verifiedEmail = sessionStorage.getItem('verified_user_email');
            
            // If we have stored data and the form exists, populate it
            if (verifiedName && this.elements.nameInput) {
                this.elements.nameInput.value = verifiedName;
                
                if (this.elements.emailInput && verifiedEmail) {
                    this.elements.emailInput.value = verifiedEmail;
                }
                
                // Make fields readonly if email is verified
                if (verifiedEmail) {
                    this.elements.nameInput.readOnly = true;
                    
                    if (this.elements.emailInput) {
                        this.elements.emailInput.readOnly = true;
                    }
                }
            }
            
            // Clear session storage after populating form
            sessionStorage.removeItem('verified_user_name');
            sessionStorage.removeItem('verified_user_email');
        }
    };
})();
