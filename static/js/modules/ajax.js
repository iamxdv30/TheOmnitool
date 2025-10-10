/**
 * ajax.js - AJAX request handling module
 * Provides a wrapper for fetch API with CSRF protection for Flask
 */

const AjaxModule = (function() {
    'use strict';
    
    /**
     * Get CSRF token from meta tag
     * @return {string} - CSRF token
     */
    function getCsrfToken() {
        return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
    }
    
    /**
     * Make an AJAX request with proper CSRF handling
     * @param {string} url - The URL to request
     * @param {Object} options - Request options
     * @return {Promise} - Fetch promise
     */
    function request(url, options = {}) {
        // Default options
        const defaults = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        };
        
        // Merge options
        const requestOptions = Object.assign({}, defaults, options);
        
        // Add CSRF token for non-GET requests
        if (requestOptions.method !== 'GET') {
            requestOptions.headers['X-CSRFToken'] = getCsrfToken();
        }
        
        // Convert body to JSON string if it's an object
        if (requestOptions.body && typeof requestOptions.body === 'object') {
            requestOptions.body = JSON.stringify(requestOptions.body);
        }
        
        // Make the request
        return fetch(url, requestOptions)
            .then(response => {
                // Check if response is JSON
                const contentType = response.headers.get('content-type');
                const isJson = contentType && contentType.includes('application/json');
                
                // Handle response based on status
                if (!response.ok) {
                    // Try to parse error response
                    return (isJson ? response.json() : response.text())
                        .then(data => {
                            throw {
                                status: response.status,
                                statusText: response.statusText,
                                data: data
                            };
                        });
                }
                
                // Parse successful response
                return isJson ? response.json() : response.text();
            })
            .catch(error => {
                // Log error and rethrow
                console.error('AJAX Error:', error);
                throw error;
            });
    }
    
    /**
     * Shorthand for GET requests
     * @param {string} url - The URL to request
     * @param {Object} options - Additional options
     * @return {Promise} - Fetch promise
     */
    function get(url, options = {}) {
        return request(url, Object.assign({}, options, { method: 'GET' }));
    }
    
    /**
     * Shorthand for POST requests
     * @param {string} url - The URL to request
     * @param {Object|FormData} data - The data to send
     * @param {Object} options - Additional options
     * @return {Promise} - Fetch promise
     */
    function post(url, data = {}, options = {}) {
        return request(url, Object.assign({}, options, { 
            method: 'POST',
            body: data
        }));
    }
    
    /**
     * Shorthand for PUT requests
     * @param {string} url - The URL to request
     * @param {Object} data - The data to send
     * @param {Object} options - Additional options
     * @return {Promise} - Fetch promise
     */
    function put(url, data = {}, options = {}) {
        return request(url, Object.assign({}, options, { 
            method: 'PUT',
            body: data
        }));
    }
    
    /**
     * Shorthand for DELETE requests
     * @param {string} url - The URL to request
     * @param {Object} options - Additional options
     * @return {Promise} - Fetch promise
     */
    function del(url, options = {}) {
        return request(url, Object.assign({}, options, { method: 'DELETE' }));
    }
    
    /**
     * Handle form submission via AJAX
     * @param {HTMLFormElement} form - The form to submit
     * @param {Object} options - Additional options
     * @return {Promise} - Fetch promise
     */
    function submitForm(form, options = {}) {
        const formData = new FormData(form);
        const method = (form.getAttribute('method') || 'POST').toUpperCase();
        const url = form.getAttribute('action') || window.location.href;
        
        // Convert FormData to object if content type is JSON
        let body = formData;
        if (options.headers && options.headers['Content-Type'] === 'application/json') {
            body = {};
            for (const [key, value] of formData.entries()) {
                body[key] = value;
            }
        }
        
        return request(url, Object.assign({}, options, { 
            method: method,
            body: body
        }));
    }
    
    /**
     * Load HTML content into a container element
     * @param {string} url - The URL to load content from
     * @param {string|HTMLElement} container - Container selector or element
     * @param {Object} options - Additional options
     * @return {Promise} - Fetch promise
     */
    function loadHtml(url, container, options = {}) {
        const containerElement = typeof container === 'string' 
            ? document.querySelector(container) 
            : container;
            
        if (!containerElement) {
            return Promise.reject(new Error('Container element not found'));
        }
        
        // Set headers to accept HTML
        const requestOptions = Object.assign({}, options, {
            headers: Object.assign({}, options.headers || {}, {
                'Accept': 'text/html'
            })
        });
        
        return request(url, requestOptions)
            .then(html => {
                containerElement.innerHTML = html;
                return html;
            });
    }
    
    // Public API
    return {
        request: request,
        get: get,
        post: post,
        put: put,
        delete: del,
        submitForm: submitForm,
        loadHtml: loadHtml,
        getCsrfToken: getCsrfToken
    };
})();
