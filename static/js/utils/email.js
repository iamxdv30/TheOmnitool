/**
 * email.js - Email validation and handling utilities
 * Contains functions for email validation and related operations
 */

const EmailUtils = (function() {
    'use strict';
    
    return {
        /**
         * Validates an email address format
         * @param {string} email - The email address to validate
         * @return {boolean} - True if email format is valid
         */
        isValidEmail: function(email) {
            if (!email) return false;
            
            // RFC 5322 compliant email regex
            const emailRegex = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
            return emailRegex.test(email.trim());
        },
        
        /**
         * Checks if an email domain appears to be valid
         * @param {string} email - The email address to check
         * @return {boolean} - True if domain appears valid
         */
        hasValidDomain: function(email) {
            if (!this.isValidEmail(email)) return false;
            
            const domain = email.split('@')[1];
            // Check for common invalid domains
            const invalidDomains = [
                'example.com',
                'test.com',
                'localhost',
                'invalid',
                'mailinator.com'
            ];
            
            return !invalidDomains.includes(domain.toLowerCase());
        },
        
        /**
         * Masks an email address for display (e.g., j***@example.com)
         * @param {string} email - The email address to mask
         * @return {string} - Masked email address
         */
        maskEmail: function(email) {
            if (!this.isValidEmail(email)) return email;
            
            const [username, domain] = email.split('@');
            let maskedUsername;
            
            if (username.length <= 2) {
                maskedUsername = username[0] + '*';
            } else {
                maskedUsername = username[0] + '*'.repeat(username.length - 2) + username[username.length - 1];
            }
            
            return `${maskedUsername}@${domain}`;
        },
        
        /**
         * Sends a verification email (interface to backend)
         * @param {string} email - The email address to verify
         * @param {Function} callback - Callback function after request
         */
        sendVerificationEmail: function(email, callback) {
            if (!this.isValidEmail(email)) {
                callback({ success: false, message: 'Invalid email format' });
                return;
            }
            
            // This will be implemented to call the backend API
            // during the actual migration phase
            fetch('/api/send-verification', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify({ email: email })
            })
            .then(response => response.json())
            .then(data => {
                callback(data);
            })
            .catch(error => {
                console.error('Error sending verification email:', error);
                callback({ 
                    success: false, 
                    message: 'Failed to send verification email. Please try again.'
                });
            });
        },
        
        /**
         * Gets CSRF token from cookie for secure requests
         * @return {string} - CSRF token value
         */
        getCsrfToken: function() {
            return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
        },
        
        /**
         * Checks email verification status
         * @param {string} email - The email to check
         * @param {Function} callback - Callback with status
         */
        checkVerificationStatus: function(email, callback) {
            if (!this.isValidEmail(email)) {
                callback({ verified: false, message: 'Invalid email' });
                return;
            }
            
            // This will be implemented to call the backend API
            // during the actual migration phase
            fetch(`/api/check-verification?email=${encodeURIComponent(email)}`, {
                method: 'GET',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            })
            .then(response => response.json())
            .then(data => {
                callback(data);
            })
            .catch(error => {
                console.error('Error checking verification status:', error);
                callback({ 
                    verified: false, 
                    message: 'Failed to check verification status'
                });
            });
        }
    };
})();
