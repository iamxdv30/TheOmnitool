/**
 * common.js - Shared utility functions for OmniTool
 * Contains common functions used across multiple pages
 */

(function(window) {
    'use strict';

    const OmniUtils = {
        /**
         * Validates if a string is empty
         * @param {string} str - The string to check
         * @return {boolean} - True if string is empty or only whitespace
         */
        isEmpty: function(str) {
            return (!str || str.trim().length === 0);
        },

        /**
         * Shows a flash message
         * @param {string} message - The message to display
         * @param {string} type - The message type (success, error, info, warning)
         * @param {number} duration - How long to show the message (ms)
         */
        showFlashMessage: function(message, type = 'info', duration = 5000) {
            const container = document.querySelector('.flash-messages');
            if (!container) return;

            const messageElement = document.createElement('div');
            messageElement.className = `alert alert-${type} alert-dismissible fade show`;
            messageElement.role = 'alert';

            messageElement.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            `;

            container.appendChild(messageElement);

            if (duration > 0) {
                setTimeout(() => {
                    const alert = new bootstrap.Alert(messageElement);
                    alert.close();
                }, duration);
            }
        },

        /**
         * Formats a date object to a readable string
         * @param {Date} date - The date to format
         * @return {string} - Formatted date string
         */
        formatDate: function(date) {
            if (!(date instanceof Date)) {
                date = new Date(date);
            }
            return date.toLocaleDateString(undefined, {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        },

        /**
         * Debounce function to limit how often a function is called
         * @param {Function} func - The function to debounce
         * @param {number} wait - The debounce wait time in ms
         * @return {Function} - Debounced function
         */
        debounce: function(func, wait = 300) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => {
                    func.apply(this, args);
                }, wait);
            };
        },

        /**
         * Safely parse JSON with error handling
         * @param {string} jsonString - The JSON string to parse
         * @param {*} fallback - Fallback value if parsing fails
         * @return {*} - Parsed object or fallback value
         */
        safeJsonParse: function(jsonString, fallback = {}) {
            try {
                return JSON.parse(jsonString);
            } catch (e) {
                console.error('Error parsing JSON:', e);
                return fallback;
            }
        },

        /**
         * Creates an event delegation handler
         * @param {string} selector - CSS selector to match elements
         * @param {string} eventType - Type of event to listen for
         * @param {Function} handler - Event handler function
         */
        delegate: function(container, selector, eventType, handler) {
            container.addEventListener(eventType, function(event) {
                const targetElement = event.target.closest(selector);
                if (targetElement) {
                    handler.call(targetElement, event);
                }
            });
        }
    };

    const EventManager = {
        init: function() {
            OmniUtils.delegate(document.body, 'click', '.delete-btn', this.handleDelete);
            OmniUtils.delegate(document.body, 'click', '.update-btn', this.handleUpdate);
            // Add more delegated events as needed
        },

        handleDelete: function(event) {
            // Implementation will be added during migration
            console.log('Delete action triggered for:', this);
        },

        handleUpdate: function(event) {
            // Implementation will be added during migration
            console.log('Update action triggered for:', this);
        }
    };

    // Expose modules to the global scope
    window.OmniUtils = OmniUtils;
    window.EventManager = EventManager;

    // Initialize EventManager when document is ready
    document.addEventListener('DOMContentLoaded', function() {
        EventManager.init();
    });

})(window);
