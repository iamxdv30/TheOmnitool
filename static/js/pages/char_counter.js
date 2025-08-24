/**
 * char_counter.js - Character Counter functionality
 * Provides real-time character counting for the character counter tool
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        CharCounter.init();
    });
    
    const CharCounter = {
        elements: {},
        maxCharacters: 3532, // Maximum characters allowed
        
        init() {
            this.cacheElements();
            this.createCountDisplay();
            this.bindEvents();
            this.updateCount(); // Initial count
        },
        
        cacheElements() {
            this.elements = {
                textarea: document.querySelector('.char-textarea'),
                form: document.querySelector('.char-form'),
                submitButton: document.querySelector('.count-button')
            };
        },
        
        createCountDisplay() {
            // Create real-time counter element
            this.elements.countDisplay = document.createElement('div');
            this.elements.countDisplay.className = 'count-display';
            
            // Insert after textarea
            if (this.elements.textarea) {
                this.elements.textarea.parentNode.insertBefore(
                    this.elements.countDisplay, 
                    this.elements.textarea.nextSibling
                );
            }
        },
        
        bindEvents() {
            if (this.elements.textarea) {
                // Update count on input
                this.elements.textarea.addEventListener('input', this.updateCount.bind(this));
                
                // Validate on form submission
                if (this.elements.form) {
                    this.elements.form.addEventListener('submit', this.validateSubmit.bind(this));
                }
            }
        },
        
        /**
         * Update character count in real-time
         */
        updateCount() {
            if (!this.elements.textarea || !this.elements.countDisplay) return;
            
            const text = this.elements.textarea.value;
            const count = text.length;
            const remaining = this.maxCharacters - count;
            
            // Update display
            this.elements.countDisplay.innerHTML = `
                <span class="count-current">Characters: ${count}</span>
                <span class="count-remaining ${remaining < 0 ? 'count-exceeded' : ''}">
                    ${remaining >= 0 ? `Remaining: ${remaining}` : `Exceeded by: ${Math.abs(remaining)}`}
                </span>
            `;
            
            // Visual feedback on textarea
            if (remaining < 0) {
                this.elements.textarea.classList.add('char-exceeded');
            } else {
                this.elements.textarea.classList.remove('char-exceeded');
            }
        },
        
        /**
         * Validate form submission
         * @param {Event} event - Submit event
         */
        validateSubmit(event) {
            if (!this.elements.textarea) return;
            
            const count = this.elements.textarea.value.length;
            
            // Allow submission even if exceeded, the server will handle the error
            // This just provides a warning
            if (count > this.maxCharacters) {
                if (!confirm(`You've exceeded the maximum character limit by ${count - this.maxCharacters} characters. Submit anyway?`)) {
                    event.preventDefault();
                }
            }
        }
    };
})();
