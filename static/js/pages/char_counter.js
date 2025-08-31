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
        maxCharacters: char_limit, // Maximum characters allowed
        
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
                submitButton: document.querySelector('.count-button'),
                charLimitInput: document.querySelector('input[name="char_limit"]')
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

                if (this.elements.charLimitInput) {
                    this.elements.charLimitInput.addEventListener('input', this.onCharLimitChange.bind(this));
                }
                
            }
        },
        
        /**
         * Update character count in real-time
         */
        onCharLimitChange(event) {
            const newLimit = parseInt(event.target.value, 10) || 0;
            if (newLimit >= 0) {
                this.maxCharacters = newLimit;
                this.updateCount();
            }
        },

        updateCount() {
            if (!this.elements.textarea || !this.elements.countDisplay) return;
            
            const text = this.elements.textarea.value;
            const count = text.length;
            const remaining = this.maxCharacters - count;
            
            // Update display
            const remainingText = remaining < 0 ? `Exceeded: ${Math.abs(remaining)}` : `Remaining: ${remaining}`;
            this.elements.countDisplay.innerHTML = `
                <span class="count-current">Characters: ${count}</span>
                <span class="count-remaining ${remaining < 0 ? 'count-exceeded' : ''}">${remainingText}</span>
            `;
            
            // Visual feedback on textarea
            if (remaining < 0) {
                this.elements.textarea.classList.add('char-exceeded');
            } else {
                this.elements.textarea.classList.remove('char-exceeded');
            }
        },
        
    };
})();
