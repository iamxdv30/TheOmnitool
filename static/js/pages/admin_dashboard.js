/**
 * admin_dashboard.js - Admin Dashboard functionality
 * Handles user search, form toggling, and UI interactions
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        AdminDashboard.init();
    });
    
    const AdminDashboard = {
        elements: {},
        
        init() {
            this.cacheElements();
            this.bindEvents();
        },
        
        cacheElements() {
            this.elements = {
                showCreateUserFormBtn: document.getElementById('showCreateUserForm'),
                createUserForm: document.getElementById('createUserForm'),
                userSearchInput: document.getElementById('userSearch'),
                userTableBody: document.getElementById('userTableBody'),
                updateFormButtons: document.querySelectorAll('.showUpdateForm'),
                toolAccessButtons: document.querySelectorAll('.showToolAccess')
            };
        },
        
        bindEvents() {
            // Toggle create user form
            if (this.elements.showCreateUserFormBtn) {
                this.elements.showCreateUserFormBtn.addEventListener('click', this.toggleCreateUserForm.bind(this));
            }
            
            // User search functionality
            if (this.elements.userSearchInput) {
                this.elements.userSearchInput.addEventListener('keyup', this.handleUserSearch.bind(this));
            }
            
            // Update form toggle buttons
            if (this.elements.updateFormButtons) {
                this.elements.updateFormButtons.forEach(button => {
                    button.addEventListener('click', this.toggleUpdateForm.bind(this));
                });
            }
            
            // Tool access toggle buttons
            if (this.elements.toolAccessButtons) {
                this.elements.toolAccessButtons.forEach(button => {
                    button.addEventListener('click', this.toggleToolAccess.bind(this));
                });
            }
        },
        
        /**
         * Toggle create user form visibility
         */
        toggleCreateUserForm() {
            if (this.elements.createUserForm) {
                const form = this.elements.createUserForm;
                form.style.display = form.style.display === 'none' ? 'block' : 'none';
            }
        },
        
        /**
         * Handle user search functionality
         * @param {Event} event - Keyup event
         */
        handleUserSearch(event) {
            const filter = event.target.value.toLowerCase();
            const rows = this.elements.userTableBody.getElementsByClassName('user-row');
            
            for (let i = 0; i < rows.length; i++) {
                const username = rows[i].getElementsByTagName('td')[0].textContent.toLowerCase();
                const email = rows[i].getElementsByTagName('td')[1].textContent.toLowerCase();
                
                if (username.indexOf(filter) > -1 || email.indexOf(filter) > -1) {
                    rows[i].style.display = '';
                } else {
                    rows[i].style.display = 'none';
                }
            }
        },
        
        /**
         * Toggle update form visibility
         * @param {Event} event - Click event
         */
        toggleUpdateForm(event) {
            const updateFormRow = event.target.closest('tr').nextElementSibling;
            updateFormRow.style.display = updateFormRow.style.display === 'none' ? 'table-row' : 'none';
        },
        
        /**
         * Toggle tool access form visibility
         * @param {Event} event - Click event
         */
        toggleToolAccess(event) {
            const toolAccessRow = event.target.closest('tr').nextElementSibling.nextElementSibling;
            toolAccessRow.style.display = toolAccessRow.style.display === 'none' ? 'table-row' : 'none';
        }
    };
})();
