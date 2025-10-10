/**
 * Provides utility functions for UI interactions and feedback
 */

(function() {
    'use strict';
    
    window.OmniUtils = window.OmniUtils || {};
    
    // Flash message functions
    window.OmniUtils.showFlashMessage = function(message, type = 'info', duration = 5000) {
        // Create flash message container if it doesn't exist
        let flashContainer = document.querySelector('.flash-messages');
        
        if (!flashContainer) {
            flashContainer = document.createElement('div');
            flashContainer.className = 'flash-messages';
            document.body.insertBefore(flashContainer, document.body.firstChild);
        }
        
        // Create the message element
        const msgElement = document.createElement('div');
        msgElement.className = `flash-message ${type}`;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'flash-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.addEventListener('click', () => removeMessage(msgElement));
        
        const content = document.createElement('span');
        content.className = 'flash-content';
        content.textContent = message;
        
        msgElement.appendChild(content);
        msgElement.appendChild(closeBtn);
        flashContainer.appendChild(msgElement);
        
        // Add visible class for animation
        setTimeout(() => {
            msgElement.classList.add('visible');
        }, 10);
        
        // Auto-remove after duration
        const timerId = setTimeout(() => removeMessage(msgElement), duration);
        msgElement.dataset.timerId = timerId;
        
        // Helper function to remove message
        function removeMessage(element) {
            // Clear the timeout if it exists
            if (element.dataset.timerId) {
                clearTimeout(parseInt(element.dataset.timerId));
            }
            
            // Remove visible class for animation
            element.classList.remove('visible');
            
            // Remove from DOM after animation
            setTimeout(() => {
                if (element.parentNode) {
                    element.parentNode.removeChild(element);
                }
                
                // Remove container if empty
                if (flashContainer && flashContainer.childNodes.length === 0) {
                    flashContainer.parentNode.removeChild(flashContainer);
                }
            }, 300);
        }
        
        return msgElement;
    };
    
    // Form utility functions
    window.OmniUtils.validateField = function(field, options = {}) {
        const value = field.value.trim();
        const name = field.name || field.id || 'Field';
        
        // Required check
        if (options.required && !value) {
            return {
                valid: false,
                message: options.requiredMessage || `${name} is required.`
            };
        }
        
        // Min length check
        if (options.minLength && value.length < options.minLength) {
            return {
                valid: false,
                message: options.minLengthMessage || 
                    `${name} must be at least ${options.minLength} characters.`
            };
        }
        
        // Max length check
        if (options.maxLength && value.length > options.maxLength) {
            return {
                valid: false,
                message: options.maxLengthMessage || 
                    `${name} must be less than ${options.maxLength} characters.`
            };
        }
        
        // Pattern check
        if (options.pattern && !options.pattern.test(value)) {
            return {
                valid: false,
                message: options.patternMessage || `${name} format is invalid.`
            };
        }
        
        // Custom validation
        if (options.validator && typeof options.validator === 'function') {
            const result = options.validator(value);
            if (result !== true) {
                return {
                    valid: false,
                    message: result || `${name} is invalid.`
                };
            }
        }
        
        return { valid: true };
    };
    
    // DOM utility functions
    window.OmniUtils.createElement = function(tag, attributes = {}, children = []) {
        const element = document.createElement(tag);
        
        // Set attributes
        Object.entries(attributes).forEach(([key, value]) => {
            if (key === 'className') {
                element.className = value;
            } else if (key === 'style' && typeof value === 'object') {
                Object.entries(value).forEach(([prop, val]) => {
                    element.style[prop] = val;
                });
            } else if (key.startsWith('on') && typeof value === 'function') {
                const event = key.slice(2).toLowerCase();
                element.addEventListener(event, value);
            } else {
                element.setAttribute(key, value);
            }
        });
        
        // Add children
        if (typeof children === 'string') {
            element.textContent = children;
        } else if (Array.isArray(children)) {
            children.forEach(child => {
                if (typeof child === 'string') {
                    element.appendChild(document.createTextNode(child));
                } else if (child instanceof Node) {
                    element.appendChild(child);
                }
            });
        }
        
        return element;
    };
    
})();
