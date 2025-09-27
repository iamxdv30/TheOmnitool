/**
 * Provides utility functions for making AJAX requests
 */

(function() {
    'use strict';
    
    window.AjaxUtils = {
        /**
         * Make a GET request
         * @param {string} url - The URL to request
         * @param {Object} params - Query parameters to append
         * @returns {Promise} - Promise resolving to the response data
         */
        get(url, params = {}) {
            const queryString = this._buildQueryString(params);
            const fullUrl = queryString ? `${url}?${queryString}` : url;
            
            return fetch(fullUrl, {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            }).then(this._handleResponse);
        },
        
        /**
         * Make a POST request
         * @param {string} url - The URL to request
         * @param {Object} data - Data to send
         * @returns {Promise} - Promise resolving to the response data
         */
        post(url, data = {}) {
            const formData = new FormData();
            
            // Add data to FormData
            Object.keys(data).forEach(key => {
                formData.append(key, data[key]);
            });
            
            return fetch(url, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            }).then(this._handleResponse);
        },
        
        /**
         * Make a POST request with JSON data
         * @param {string} url - The URL to request
         * @param {Object} data - JSON data to send
         * @returns {Promise} - Promise resolving to the response data
         */
        postJson(url, data = {}) {
            return fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            }).then(this._handleResponse);
        },
        
        /**
         * Handle fetch response
         * @private
         * @param {Response} response - Fetch Response object
         * @returns {Promise} - Promise resolving to the response data
         */
        _handleResponse(response) {
            if (response.redirected) {
                window.location.href = response.url;
                return Promise.reject(new Error('Redirected'));
            }
            
            if (!response.ok) {
                return response.json()
                    .then(data => Promise.reject(data))
                    .catch(() => Promise.reject({
                        message: `HTTP error! status: ${response.status}`
                    }));
            }
            
            const contentType = response.headers.get('content-type');
            
            if (contentType && contentType.includes('application/json')) {
                return response.json();
            }
            
            return response.text();
        },
        
        /**
         * Build query string from parameters
         * @private
         * @param {Object} params - Query parameters
         * @returns {string} - Encoded query string
         */
        _buildQueryString(params) {
            return Object.keys(params)
                .filter(key => params[key] !== undefined && params[key] !== null)
                .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
                .join('&');
        }
    };
    
})();
