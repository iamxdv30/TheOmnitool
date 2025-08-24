/**
 * superadmin_dashboard.js - Superadmin Dashboard functionality
 * Handles user management, system stats, and admin operations
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        SuperadminDashboard.init();
    });
    
    const SuperadminDashboard = {
        elements: {},
        users: [],
        stats: {},
        currentPage: 1,
        itemsPerPage: 10,
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.loadDashboardData();
            this.initCharts();
        },
        
        cacheElements() {
            this.elements = {
                userTable: document.getElementById('userTable'),
                userTableBody: document.getElementById('userTableBody'),
                pagination: document.getElementById('userPagination'),
                statsCards: document.querySelectorAll('.stat-card'),
                searchInput: document.getElementById('searchUsers'),
                userRoleFilter: document.getElementById('userRoleFilter'),
                userStatusFilter: document.getElementById('userStatusFilter'),
                refreshStatsBtn: document.getElementById('refreshStatsBtn'),
                userModal: document.getElementById('userModal'),
                userForm: document.getElementById('userForm'),
                newUserBtn: document.getElementById('newUserBtn'),
                exportUsersBtn: document.getElementById('exportUsersBtn'),
                systemLogsBtn: document.getElementById('systemLogsBtn'),
                logsModal: document.getElementById('logsModal'),
                logsContent: document.getElementById('logsContent')
            };
        },
        
        bindEvents() {
            if (this.elements.searchInput) {
                this.elements.searchInput.addEventListener('input', OmniUtils.debounce(this.handleSearch.bind(this), 300));
            }
            
            if (this.elements.userRoleFilter) {
                this.elements.userRoleFilter.addEventListener('change', this.filterUsers.bind(this));
            }
            
            if (this.elements.userStatusFilter) {
                this.elements.userStatusFilter.addEventListener('change', this.filterUsers.bind(this));
            }
            
            if (this.elements.refreshStatsBtn) {
                this.elements.refreshStatsBtn.addEventListener('click', this.refreshStats.bind(this));
            }
            
            if (this.elements.newUserBtn) {
                this.elements.newUserBtn.addEventListener('click', this.showUserModal.bind(this));
            }
            
            if (this.elements.userForm) {
                this.elements.userForm.addEventListener('submit', this.handleUserFormSubmit.bind(this));
            }
            
            if (this.elements.exportUsersBtn) {
                this.elements.exportUsersBtn.addEventListener('click', this.exportUsers.bind(this));
            }
            
            if (this.elements.systemLogsBtn) {
                this.elements.systemLogsBtn.addEventListener('click', this.showSystemLogs.bind(this));
            }
        },
        
        /**
         * Load dashboard data including users and stats
         */
        loadDashboardData() {
            // Show loading state
            if (this.elements.userTableBody) {
                this.elements.userTableBody.innerHTML = '<tr><td colspan="6" class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></td></tr>';
            }
            
            // Load stats
            this.loadStats();
            
            // Load users
            AjaxModule.get('/api/admin/users')
                .then(data => {
                    this.users = data.users || [];
                    this.renderUsers();
                })
                .catch(error => {
                    console.error('Error loading users:', error);
                    if (this.elements.userTableBody) {
                        this.elements.userTableBody.innerHTML = '<tr><td colspan="6" class="text-center text-danger">Failed to load users. Please try again later.</td></tr>';
                    }
                });
        },
        
        /**
         * Load system statistics
         */
        loadStats() {
            AjaxModule.get('/api/admin/stats')
                .then(data => {
                    this.stats = data;
                    this.updateStatsCards();
                    this.updateCharts();
                })
                .catch(error => {
                    console.error('Error loading stats:', error);
                    OmniUtils.showFlashMessage('Failed to load system statistics', 'error');
                });
        },
        
        /**
         * Update stats cards with latest data
         */
        updateStatsCards() {
            if (!this.elements.statsCards || !this.stats) return;
            
            const statsMap = {
                'total-users': this.stats.totalUsers || 0,
                'active-users': this.stats.activeUsers || 0,
                'tools-used': this.stats.toolsUsed || 0,
                'total-requests': this.stats.totalRequests || 0
            };
            
            this.elements.statsCards.forEach(card => {
                const statType = card.getAttribute('data-stat-type');
                const valueElement = card.querySelector('.stat-value');
                
                if (statType && valueElement && statsMap[statType] !== undefined) {
                    valueElement.textContent = statsMap[statType].toLocaleString();
                }
            });
        },
        
        /**
         * Initialize dashboard charts
         */
        initCharts() {
            // This will be implemented when charts are needed
            // Using Chart.js or similar library
        },
        
        /**
         * Update charts with latest data
         */
        updateCharts() {
            // This will be implemented when charts are needed
        },
        
        /**
         * Render users table with pagination
         * @param {Array} filteredUsers - Optional filtered users array
         */
        renderUsers(filteredUsers) {
            if (!this.elements.userTableBody) return;
            
            const users = filteredUsers || this.users;
            
            if (users.length === 0) {
                this.elements.userTableBody.innerHTML = '<tr><td colspan="6" class="text-center">No users found.</td></tr>';
                this.renderPagination(0);
                return;
            }
            
            // Calculate pagination
            const totalPages = Math.ceil(users.length / this.itemsPerPage);
            const startIndex = (this.currentPage - 1) * this.itemsPerPage;
            const endIndex = Math.min(startIndex + this.itemsPerPage, users.length);
            const pageUsers = users.slice(startIndex, endIndex);
            
            // Render table rows
            let html = '';
            
            pageUsers.forEach(user => {
                const statusClass = user.isActive ? 'text-success' : 'text-danger';
                const statusText = user.isActive ? 'Active' : 'Inactive';
                
                html += `
                    <tr data-user-id="${user.id}">
                        <td>${user.id}</td>
                        <td>${user.username}</td>
                        <td>${user.email}</td>
                        <td>${user.role}</td>
                        <td><span class="${statusClass}">${statusText}</span></td>
                        <td>
                            <div class="btn-group btn-group-sm" role="group">
                                <button type="button" class="btn btn-outline-primary edit-user" data-id="${user.id}">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button type="button" class="btn btn-outline-${user.isActive ? 'warning' : 'success'} toggle-status" data-id="${user.id}">
                                    <i class="fas fa-${user.isActive ? 'ban' : 'check'}"></i>
                                </button>
                                <button type="button" class="btn btn-outline-danger delete-user" data-id="${user.id}">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            });
            
            this.elements.userTableBody.innerHTML = html;
            
            // Render pagination
            this.renderPagination(totalPages);
            
            // Add event listeners to action buttons
            const editButtons = this.elements.userTableBody.querySelectorAll('.edit-user');
            editButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const userId = e.currentTarget.getAttribute('data-id');
                    this.editUser(userId);
                });
            });
            
            const toggleButtons = this.elements.userTableBody.querySelectorAll('.toggle-status');
            toggleButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const userId = e.currentTarget.getAttribute('data-id');
                    this.toggleUserStatus(userId);
                });
            });
            
            const deleteButtons = this.elements.userTableBody.querySelectorAll('.delete-user');
            deleteButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const userId = e.currentTarget.getAttribute('data-id');
                    this.deleteUser(userId);
                });
            });
        },
        
        /**
         * Render pagination controls
         * @param {number} totalPages - Total number of pages
         */
        renderPagination(totalPages) {
            if (!this.elements.pagination) return;
            
            if (totalPages <= 1) {
                this.elements.pagination.innerHTML = '';
                return;
            }
            
            let html = '<ul class="pagination justify-content-center">';
            
            // Previous button
            html += `
                <li class="page-item ${this.currentPage === 1 ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${this.currentPage - 1}" aria-label="Previous">
                        <span aria-hidden="true">&laquo;</span>
                    </a>
                </li>
            `;
            
            // Page numbers
            const maxPages = 5;
            let startPage = Math.max(1, this.currentPage - Math.floor(maxPages / 2));
            let endPage = Math.min(totalPages, startPage + maxPages - 1);
            
            if (endPage - startPage + 1 < maxPages) {
                startPage = Math.max(1, endPage - maxPages + 1);
            }
            
            for (let i = startPage; i <= endPage; i++) {
                html += `
                    <li class="page-item ${i === this.currentPage ? 'active' : ''}">
                        <a class="page-link" href="#" data-page="${i}">${i}</a>
                    </li>
                `;
            }
            
            // Next button
            html += `
                <li class="page-item ${this.currentPage === totalPages ? 'disabled' : ''}">
                    <a class="page-link" href="#" data-page="${this.currentPage + 1}" aria-label="Next">
                        <span aria-hidden="true">&raquo;</span>
                    </a>
                </li>
            `;
            
            html += '</ul>';
            this.elements.pagination.innerHTML = html;
            
            // Add event listeners to pagination links
            const pageLinks = this.elements.pagination.querySelectorAll('.page-link');
            pageLinks.forEach(link => {
                link.addEventListener('click', (e) => {
                    e.preventDefault();
                    const page = parseInt(e.currentTarget.getAttribute('data-page'));
                    if (page && page !== this.currentPage) {
                        this.currentPage = page;
                        this.renderUsers();
                    }
                });
            });
        },
        
        /**
         * Handle search input
         */
        handleSearch() {
            const searchTerm = this.elements.searchInput.value.toLowerCase();
            this.filterUsers();
        },
        
        /**
         * Filter users based on search, role, and status
         */
        filterUsers() {
            const searchTerm = this.elements.searchInput?.value.toLowerCase() || '';
            const roleFilter = this.elements.userRoleFilter?.value || '';
            const statusFilter = this.elements.userStatusFilter?.value || '';
            
            // Reset to first page
            this.currentPage = 1;
            
            // Apply filters
            const filteredUsers = this.users.filter(user => {
                // Search filter
                const matchesSearch = searchTerm === '' || 
                    user.username.toLowerCase().includes(searchTerm) || 
                    user.email.toLowerCase().includes(searchTerm);
                
                // Role filter
                const matchesRole = roleFilter === '' || user.role === roleFilter;
                
                // Status filter
                const matchesStatus = statusFilter === '' || 
                    (statusFilter === 'active' && user.isActive) || 
                    (statusFilter === 'inactive' && !user.isActive);
                
                return matchesSearch && matchesRole && matchesStatus;
            });
            
            this.renderUsers(filteredUsers);
        },
        
        /**
         * Refresh system statistics
         */
        refreshStats() {
            if (this.elements.refreshStatsBtn) {
                this.elements.refreshStatsBtn.disabled = true;
                this.elements.refreshStatsBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Refreshing...';
            }
            
            this.loadStats();
            
            setTimeout(() => {
                if (this.elements.refreshStatsBtn) {
                    this.elements.refreshStatsBtn.disabled = false;
                    this.elements.refreshStatsBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh Stats';
                }
            }, 1000);
        },
        
        /**
         * Show user modal for creating or editing a user
         * @param {string} userId - Optional user ID for editing
         */
        showUserModal(userId) {
            // Implementation will be added during migration
            UIModule.showModal(this.elements.userModal);
        },
        
        /**
         * Handle user form submission
         * @param {Event} event - Submit event
         */
        handleUserFormSubmit(event) {
            event.preventDefault();
            // Implementation will be added during migration
        },
        
        /**
         * Edit a user
         * @param {string} userId - User ID to edit
         */
        editUser(userId) {
            const user = this.users.find(u => u.id === userId);
            if (!user) return;
            
            this.showUserModal(userId);
        },
        
        /**
         * Toggle user active status
         * @param {string} userId - User ID to toggle
         */
        toggleUserStatus(userId) {
            const user = this.users.find(u => u.id === userId);
            if (!user) return;
            
            const newStatus = !user.isActive;
            const action = newStatus ? 'activate' : 'deactivate';
            
            UIModule.confirmDialog({
                title: `${action.charAt(0).toUpperCase() + action.slice(1)} User`,
                message: `Are you sure you want to ${action} this user?`,
                confirmText: 'Confirm',
                confirmButtonClass: newStatus ? 'btn-success' : 'btn-warning'
            }).then(confirmed => {
                if (!confirmed) return;
                
                AjaxModule.put(`/api/admin/users/${userId}/status`, { isActive: newStatus })
                    .then(response => {
                        OmniUtils.showFlashMessage(`User ${action}d successfully!`, 'success');
                        
                        // Update user in local array
                        user.isActive = newStatus;
                        
                        // Re-render users
                        this.renderUsers();
                    })
                    .catch(error => {
                        console.error(`Error ${action}ing user:`, error);
                        OmniUtils.showFlashMessage(`Failed to ${action} user. Please try again later.`, 'error');
                    });
            });
        },
        
        /**
         * Delete a user
         * @param {string} userId - User ID to delete
         */
        deleteUser(userId) {
            UIModule.confirmDialog({
                title: 'Delete User',
                message: 'Are you sure you want to delete this user? This action cannot be undone.',
                confirmText: 'Delete',
                confirmButtonClass: 'btn-danger'
            }).then(confirmed => {
                if (!confirmed) return;
                
                AjaxModule.delete(`/api/admin/users/${userId}`)
                    .then(response => {
                        OmniUtils.showFlashMessage('User deleted successfully!', 'success');
                        
                        // Remove user from local array
                        this.users = this.users.filter(u => u.id !== userId);
                        
                        // Re-render users
                        this.renderUsers();
                    })
                    .catch(error => {
                        console.error('Error deleting user:', error);
                        OmniUtils.showFlashMessage('Failed to delete user. Please try again later.', 'error');
                    });
            });
        },
        
        /**
         * Export users to CSV
         */
        exportUsers() {
            // Implementation will be added during migration
        },
        
        /**
         * Show system logs modal
         */
        showSystemLogs() {
            if (!this.elements.logsModal || !this.elements.logsContent) return;
            
            // Show loading state
            this.elements.logsContent.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            
            // Show modal
            UIModule.showModal(this.elements.logsModal);
            
            // Fetch logs
            AjaxModule.get('/api/admin/logs')
                .then(data => {
                    const logs = data.logs || [];
                    
                    if (logs.length === 0) {
                        this.elements.logsContent.innerHTML = '<div class="alert alert-info">No logs found.</div>';
                        return;
                    }
                    
                    let html = '<div class="logs-container">';
                    
                    logs.forEach(log => {
                        const levelClass = {
                            'ERROR': 'text-danger',
                            'WARNING': 'text-warning',
                            'INFO': 'text-info',
                            'DEBUG': 'text-secondary'
                        }[log.level] || '';
                        
                        html += `
                            <div class="log-entry">
                                <div class="log-timestamp">${OmniUtils.formatDate(log.timestamp)}</div>
                                <div class="log-level ${levelClass}">${log.level}</div>
                                <div class="log-message">${log.message}</div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                    this.elements.logsContent.innerHTML = html;
                })
                .catch(error => {
                    console.error('Error loading logs:', error);
                    this.elements.logsContent.innerHTML = '<div class="alert alert-danger">Failed to load logs. Please try again later.</div>';
                });
        }
    };
})();
