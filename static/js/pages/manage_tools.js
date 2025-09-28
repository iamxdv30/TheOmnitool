/**
 * manage_tools.js - Tool Management functionality
 * Handles CRUD operations for tools, categories, and tool settings
 */

(function() {
    'use strict';
    
    // Module initialization
    document.addEventListener('DOMContentLoaded', function() {
        ManageTools.init();
    });
    
    const ManageTools = {
        elements: {},
        tools: [],
        categories: [],
        currentToolId: null,
        
        init() {
            this.cacheElements();
            this.bindEvents();
            this.loadTools();
            this.loadCategories();
        },
        
        cacheElements() {
            this.elements = {
                // Tool list elements
                toolList: document.getElementById('toolList'),
                toolSearch: document.getElementById('searchTools'),
                categoryFilter: document.getElementById('categoryFilter'),
                statusFilter: document.getElementById('statusFilter'),
                
                // Tool form elements
                toolForm: document.getElementById('toolForm'),
                toolNameInput: document.getElementById('toolName'),
                toolDescriptionInput: document.getElementById('toolDescription'),
                toolCategorySelect: document.getElementById('toolCategory'),
                toolStatusSelect: document.getElementById('toolStatus'),
                toolIconInput: document.getElementById('toolIcon'),
                toolUrlInput: document.getElementById('toolUrl'),
                toolIsPublicCheckbox: document.getElementById('toolIsPublic'),
                toolRequiresAuthCheckbox: document.getElementById('toolRequiresAuth'),
                saveToolBtn: document.getElementById('saveToolBtn'),
                newToolBtn: document.getElementById('newToolBtn'),
                
                // Category management elements
                categoryForm: document.getElementById('categoryForm'),
                categoryNameInput: document.getElementById('categoryName'),
                categoryDescriptionInput: document.getElementById('categoryDescription'),
                categoryIconInput: document.getElementById('categoryIcon'),
                saveCategoryBtn: document.getElementById('saveCategoryBtn'),
                categoryList: document.getElementById('categoryList'),
                
                // Modals
                toolModal: document.getElementById('toolModal'),
                categoryModal: document.getElementById('categoryModal'),
                confirmModal: document.getElementById('confirmModal'),
                
                // Stats elements
                toolStatsContainer: document.getElementById('toolStats'),
                
                // Batch actions
                batchActionsBtn: document.getElementById('batchActionsBtn'),
                batchActionsList: document.getElementById('batchActionsList')
            };
        },
        
        bindEvents() {
            // Tool search and filters
            if (this.elements.toolSearch) {
                this.elements.toolSearch.addEventListener('input', OmniUtils.debounce(this.filterTools.bind(this), 300));
            }
            
            if (this.elements.categoryFilter) {
                this.elements.categoryFilter.addEventListener('change', this.filterTools.bind(this));
            }
            
            if (this.elements.statusFilter) {
                this.elements.statusFilter.addEventListener('change', this.filterTools.bind(this));
            }
            
            // Tool form
            if (this.elements.toolForm) {
                this.elements.toolForm.addEventListener('submit', this.handleToolFormSubmit.bind(this));
            }
            
            if (this.elements.newToolBtn) {
                this.elements.newToolBtn.addEventListener('click', this.resetToolForm.bind(this));
            }
            
            // Category form
            if (this.elements.categoryForm) {
                this.elements.categoryForm.addEventListener('submit', this.handleCategoryFormSubmit.bind(this));
            }
            
            // Batch actions
            if (this.elements.batchActionsBtn) {
                this.elements.batchActionsBtn.addEventListener('click', this.toggleBatchActions.bind(this));
            }
            
            // Batch action items
            if (this.elements.batchActionsList) {
                const batchActions = this.elements.batchActionsList.querySelectorAll('.dropdown-item');
                batchActions.forEach(action => {
                    action.addEventListener('click', this.handleBatchAction.bind(this));
                });
            }
        },
        
        /**
         * Load all tools
         */
        loadTools() {
            if (!this.elements.toolList) return;
            
            // Show loading state
            this.elements.toolList.innerHTML = '<div class="text-center py-4"><div class="spinner-border" role="status"><span class="visually-hidden">Loading...</span></div></div>';
            
            // Fetch tools from server
            AjaxModule.get('/api/tools')
                .then(data => {
                    this.tools = data.tools || [];
                    this.renderToolList();
                })
                .catch(error => {
                    console.error('Error loading tools:', error);
                    this.elements.toolList.innerHTML = '<div class="alert alert-danger">Failed to load tools. Please try again later.</div>';
                });
        },
        
        /**
         * Load all categories
         */
        loadCategories() {
            // Fetch categories from server
            AjaxModule.get('/api/tool-categories')
                .then(data => {
                    this.categories = data.categories || [];
                    this.populateCategoryDropdowns();
                    this.renderCategoryList();
                })
                .catch(error => {
                    console.error('Error loading categories:', error);
                    OmniUtils.showFlashMessage('Failed to load tool categories', 'error');
                });
        },
        
        /**
         * Populate category dropdowns with options
         */
        populateCategoryDropdowns() {
            // Populate category filter
            if (this.elements.categoryFilter) {
                let html = '<option value="">All Categories</option>';
                
                this.categories.forEach(category => {
                    html += `<option value="${category.id}">${category.name}</option>`;
                });
                
                this.elements.categoryFilter.innerHTML = html;
            }
            
            // Populate tool form category select
            if (this.elements.toolCategorySelect) {
                let html = '<option value="">Select Category</option>';
                
                this.categories.forEach(category => {
                    html += `<option value="${category.id}">${category.name}</option>`;
                });
                
                this.elements.toolCategorySelect.innerHTML = html;
            }
        },
        
        /**
         * Render the tool list
         * @param {Array} filteredTools - Optional filtered tools array
         */
        renderToolList(filteredTools) {
            if (!this.elements.toolList) return;
            
            const tools = filteredTools || this.tools;
            
            if (tools.length === 0) {
                this.elements.toolList.innerHTML = '<div class="alert alert-info">No tools found.</div>';
                return;
            }
            
            let html = '<div class="row">';
            
            tools.forEach(tool => {
                const statusClass = tool.isActive ? 'bg-success' : 'bg-secondary';
                const categoryName = this.getCategoryName(tool.categoryId);
                
                html += `
                    <div class="col-md-6 col-lg-4 mb-4">
                        <div class="card h-100 tool-card" data-tool-id="${tool.id}">
                            <div class="card-status-indicator ${statusClass}"></div>
                            <div class="card-body">
                                <div class="d-flex justify-content-between align-items-start mb-2">
                                    <h5 class="card-title mb-0">
                                        <i class="${tool.icon || 'fas fa-tools'}"></i> ${tool.name}
                                    </h5>
                                    <span class="badge bg-primary">${categoryName}</span>
                                </div>
                                <p class="card-text">${tool.description}</p>
                                <div class="tool-meta">
                                    <small class="text-muted">
                                        <i class="fas fa-eye"></i> ${tool.isPublic ? 'Public' : 'Private'} |
                                        <i class="fas fa-lock"></i> ${tool.requiresAuth ? 'Auth Required' : 'No Auth'}
                                    </small>
                                </div>
                            </div>
                            <div class="card-footer bg-transparent">
                                <div class="btn-group w-100" role="group">
                                    <button type="button" class="btn btn-sm btn-outline-primary edit-tool" data-id="${tool.id}">
                                        <i class="fas fa-edit"></i> Edit
                                    </button>
                                    <button type="button" class="btn btn-sm btn-outline-${tool.isActive ? 'warning' : 'success'} toggle-status" data-id="${tool.id}">
                                        <i class="fas fa-${tool.isActive ? 'pause' : 'play'}"></i> ${tool.isActive ? 'Disable' : 'Enable'}
                                    </button>
                                    <button type="button" class="btn btn-sm btn-outline-danger delete-tool" data-id="${tool.id}">
                                        <i class="fas fa-trash"></i> Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            this.elements.toolList.innerHTML = html;
            
            // Add event listeners to tool cards
            const editButtons = this.elements.toolList.querySelectorAll('.edit-tool');
            editButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const toolId = e.currentTarget.getAttribute('data-id');
                    this.editTool(toolId);
                });
            });
            
            const toggleButtons = this.elements.toolList.querySelectorAll('.toggle-status');
            toggleButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const toolId = e.currentTarget.getAttribute('data-id');
                    this.toggleToolStatus(toolId);
                });
            });
            
            const deleteButtons = this.elements.toolList.querySelectorAll('.delete-tool');
            deleteButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const toolId = e.currentTarget.getAttribute('data-id');
                    this.deleteTool(toolId);
                });
            });
        },
        
        /**
         * Render the category list
         */
        renderCategoryList() {
            if (!this.elements.categoryList) return;
            
            if (this.categories.length === 0) {
                this.elements.categoryList.innerHTML = '<div class="alert alert-info">No categories found.</div>';
                return;
            }
            
            let html = '<div class="list-group">';
            
            this.categories.forEach(category => {
                html += `
                    <div class="list-group-item d-flex justify-content-between align-items-center">
                        <div>
                            <i class="${category.icon || 'fas fa-folder'}"></i>
                            <strong>${category.name}</strong>
                            <p class="mb-0 small text-muted">${category.description || 'No description'}</p>
                        </div>
                        <div class="btn-group btn-group-sm" role="group">
                            <button type="button" class="btn btn-outline-primary edit-category" data-id="${category.id}">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button type="button" class="btn btn-outline-danger delete-category" data-id="${category.id}">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `;
            });
            
            html += '</div>';
            this.elements.categoryList.innerHTML = html;
            
            // Add event listeners to category items
            const editButtons = this.elements.categoryList.querySelectorAll('.edit-category');
            editButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const categoryId = e.currentTarget.getAttribute('data-id');
                    this.editCategory(categoryId);
                });
            });
            
            const deleteButtons = this.elements.categoryList.querySelectorAll('.delete-category');
            deleteButtons.forEach(button => {
                button.addEventListener('click', (e) => {
                    const categoryId = e.currentTarget.getAttribute('data-id');
                    this.deleteCategory(categoryId);
                });
            });
        },
        
        /**
         * Filter tools based on search, category, and status
         */
        filterTools() {
            const searchTerm = this.elements.toolSearch?.value.toLowerCase() || '';
            const categoryFilter = this.elements.categoryFilter?.value || '';
            const statusFilter = this.elements.statusFilter?.value || '';
            
            // Apply filters
            const filteredTools = this.tools.filter(tool => {
                // Search filter
                const matchesSearch = searchTerm === '' || 
                    tool.name.toLowerCase().includes(searchTerm) || 
                    tool.description.toLowerCase().includes(searchTerm);
                
                // Category filter
                const matchesCategory = categoryFilter === '' || tool.categoryId === categoryFilter;
                
                // Status filter
                const matchesStatus = statusFilter === '' || 
                    (statusFilter === 'active' && tool.isActive) || 
                    (statusFilter === 'inactive' && !tool.isActive);
                
                return matchesSearch && matchesCategory && matchesStatus;
            });
            
            this.renderToolList(filteredTools);
        },
        
        /**
         * Handle tool form submission
         * @param {Event} event - Submit event
         */
        handleToolFormSubmit(event) {
            event.preventDefault();
            
            // Basic validation
            const name = this.elements.toolNameInput.value;
            const description = this.elements.toolDescriptionInput.value;
            const categoryId = this.elements.toolCategorySelect.value;
            
            if (!name || !description || !categoryId) {
                OmniUtils.showFlashMessage('Please fill in all required fields', 'error');
                return;
            }
            
            // Show loading state
            this.elements.saveToolBtn.disabled = true;
            this.elements.saveToolBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            
            const toolData = {
                name: name,
                description: description,
                categoryId: categoryId,
                status: this.elements.toolStatusSelect.value,
                icon: this.elements.toolIconInput.value,
                url: this.elements.toolUrlInput.value,
                isPublic: this.elements.toolIsPublicCheckbox.checked,
                requiresAuth: this.elements.toolRequiresAuthCheckbox.checked
            };
            
            // Determine if this is a create or update operation
            const isUpdate = !!this.currentToolId;
            const url = isUpdate 
                ? `/api/tools/${this.currentToolId}` 
                : '/api/tools';
            const method = isUpdate ? 'PUT' : 'POST';
            
            // Submit form using AJAX
            AjaxModule.request(url, {
                method: method,
                body: toolData
            })
                .then(response => {
                    // Show success message
                    OmniUtils.showFlashMessage(`Tool ${isUpdate ? 'updated' : 'created'} successfully!`, 'success');
                    
                    // Close modal
                    UIModule.hideModal(this.elements.toolModal);
                    
                    // Reload tools
                    this.loadTools();
                    
                    // Reset form for new tool
                    this.resetToolForm();
                })
                .catch(error => {
                    console.error('Error saving tool:', error);
                    
                    // Show error message
                    OmniUtils.showFlashMessage('Failed to save tool. Please try again later.', 'error');
                    
                    // Reset button state
                    this.elements.saveToolBtn.disabled = false;
                    this.elements.saveToolBtn.textContent = isUpdate ? 'Update Tool' : 'Save Tool';
                });
        },
        
        /**
         * Handle category form submission
         * @param {Event} event - Submit event
         */
        handleCategoryFormSubmit(event) {
            event.preventDefault();
            
            // Basic validation
            const name = this.elements.categoryNameInput.value;
            
            if (!name) {
                OmniUtils.showFlashMessage('Please enter a category name', 'error');
                return;
            }
            
            // Show loading state
            this.elements.saveCategoryBtn.disabled = true;
            this.elements.saveCategoryBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
            
            const categoryData = {
                name: name,
                description: this.elements.categoryDescriptionInput.value,
                icon: this.elements.categoryIconInput.value
            };
            
            // Determine if this is a create or update operation
            const isUpdate = !!this.currentCategoryId;
            const url = isUpdate 
                ? `/api/tool-categories/${this.currentCategoryId}` 
                : '/api/tool-categories';
            const method = isUpdate ? 'PUT' : 'POST';
            
            // Submit form using AJAX
            AjaxModule.request(url, {
                method: method,
                body: categoryData
            })
                .then(response => {
                    // Show success message
                    OmniUtils.showFlashMessage(`Category ${isUpdate ? 'updated' : 'created'} successfully!`, 'success');
                    
                    // Close modal
                    UIModule.hideModal(this.elements.categoryModal);
                    
                    // Reload categories
                    this.loadCategories();
                    
                    // Reset form
                    this.resetCategoryForm();
                })
                .catch(error => {
                    console.error('Error saving category:', error);
                    
                    // Show error message
                    OmniUtils.showFlashMessage('Failed to save category. Please try again later.', 'error');
                    
                    // Reset button state
                    this.elements.saveCategoryBtn.disabled = false;
                    this.elements.saveCategoryBtn.textContent = isUpdate ? 'Update Category' : 'Save Category';
                });
        },
        
        /**
         * Edit a tool
         * @param {string} toolId - Tool ID to edit
         */
        editTool(toolId) {
            const tool = this.tools.find(t => t.id === toolId);
            
            if (!tool) return;
            
            // Set form values
            this.elements.toolNameInput.value = tool.name;
            this.elements.toolDescriptionInput.value = tool.description;
            this.elements.toolCategorySelect.value = tool.categoryId;
            this.elements.toolStatusSelect.value = tool.status;
            this.elements.toolIconInput.value = tool.icon || '';
            this.elements.toolUrlInput.value = tool.url || '';
            this.elements.toolIsPublicCheckbox.checked = tool.isPublic;
            this.elements.toolRequiresAuthCheckbox.checked = tool.requiresAuth;
            
            // Set current tool ID
            this.currentToolId = toolId;
            
            // Update button text
            this.elements.saveToolBtn.textContent = 'Update Tool';
            
            // Show modal
            UIModule.showModal(this.elements.toolModal);
        },
        
        /**
         * Reset the tool form for a new tool
         */
        resetToolForm() {
            if (!this.elements.toolForm) return;
            
            this.elements.toolForm.reset();
            this.currentToolId = null;
            this.elements.saveToolBtn.textContent = 'Save Tool';
            
            // Show modal
            UIModule.showModal(this.elements.toolModal);
        },
        
        /**
         * Edit a category
         * @param {string} categoryId - Category ID to edit
         */
        editCategory(categoryId) {
            const category = this.categories.find(c => c.id === categoryId);
            
            if (!category) return;
            
            // Set form values
            this.elements.categoryNameInput.value = category.name;
            this.elements.categoryDescriptionInput.value = category.description || '';
            this.elements.categoryIconInput.value = category.icon || '';
            
            // Set current category ID
            this.currentCategoryId = categoryId;
            
            // Update button text
            this.elements.saveCategoryBtn.textContent = 'Update Category';
            
            // Show modal
            UIModule.showModal(this.elements.categoryModal);
        },
        
        /**
         * Reset the category form for a new category
         */
        resetCategoryForm() {
            if (!this.elements.categoryForm) return;
            
            this.elements.categoryForm.reset();
            this.currentCategoryId = null;
            this.elements.saveCategoryBtn.textContent = 'Save Category';
        },
        
        /**
         * Toggle tool active status
         * @param {string} toolId - Tool ID to toggle
         */
        toggleToolStatus(toolId) {
            const tool = this.tools.find(t => t.id === toolId);
            if (!tool) return;
            
            const newStatus = !tool.isActive;
            const action = newStatus ? 'enable' : 'disable';
            
            UIModule.confirmDialog({
                title: `${action.charAt(0).toUpperCase() + action.slice(1)} Tool`,
                message: `Are you sure you want to ${action} "${tool.name}"?`,
                confirmText: 'Confirm',
                confirmButtonClass: newStatus ? 'btn-success' : 'btn-warning'
            }).then(confirmed => {
                if (!confirmed) return;
                
                AjaxModule.put(`/api/tools/${toolId}/status`, { isActive: newStatus })
                    .then(response => {
                        OmniUtils.showFlashMessage(`Tool ${action}d successfully!`, 'success');
                        
                        // Update tool in local array
                        tool.isActive = newStatus;
                        
                        // Re-render tools
                        this.renderToolList();
                    })
                    .catch(error => {
                        console.error(`Error ${action}ing tool:`, error);
                        OmniUtils.showFlashMessage(`Failed to ${action} tool. Please try again later.`, 'error');
                    });
            });
        },
        
        /**
         * Delete a tool
         * @param {string} toolId - Tool ID to delete
         */
        deleteTool(toolId) {
            const tool = this.tools.find(t => t.id === toolId);
            if (!tool) return;
            
            UIModule.confirmDialog({
                title: 'Delete Tool',
                message: `Are you sure you want to delete "${tool.name}"? This action cannot be undone.`,
                confirmText: 'Delete',
                confirmButtonClass: 'btn-danger'
            }).then(confirmed => {
                if (!confirmed) return;
                
                AjaxModule.delete(`/api/tools/${toolId}`)
                    .then(response => {
                        OmniUtils.showFlashMessage('Tool deleted successfully!', 'success');
                        
                        // Remove tool from local array
                        this.tools = this.tools.filter(t => t.id !== toolId);
                        
                        // Re-render tools
                        this.renderToolList();
                    })
                    .catch(error => {
                        console.error('Error deleting tool:', error);
                        OmniUtils.showFlashMessage('Failed to delete tool. Please try again later.', 'error');
                    });
            });
        },
        
        /**
         * Delete a category
         * @param {string} categoryId - Category ID to delete
         */
        deleteCategory(categoryId) {
            const category = this.categories.find(c => c.id === categoryId);
            if (!category) return;
            
            // Check if any tools are using this category
            const toolsUsingCategory = this.tools.filter(t => t.categoryId === categoryId);
            
            if (toolsUsingCategory.length > 0) {
                OmniUtils.showFlashMessage(`Cannot delete category "${category.name}" because it is being used by ${toolsUsingCategory.length} tool(s).`, 'error');
                return;
            }
            
            UIModule.confirmDialog({
                title: 'Delete Category',
                message: `Are you sure you want to delete "${category.name}"? This action cannot be undone.`,
                confirmText: 'Delete',
                confirmButtonClass: 'btn-danger'
            }).then(confirmed => {
                if (!confirmed) return;
                
                AjaxModule.delete(`/api/tool-categories/${categoryId}`)
                    .then(response => {
                        OmniUtils.showFlashMessage('Category deleted successfully!', 'success');
                        
                        // Remove category from local array
                        this.categories = this.categories.filter(c => c.id !== categoryId);
                        
                        // Re-render categories
                        this.renderCategoryList();
                        this.populateCategoryDropdowns();
                    })
                    .catch(error => {
                        console.error('Error deleting category:', error);
                        OmniUtils.showFlashMessage('Failed to delete category. Please try again later.', 'error');
                    });
            });
        },
        
        /**
         * Get category name by ID
         * @param {string} categoryId - Category ID
         * @returns {string} Category name or 'Uncategorized'
         */
        getCategoryName(categoryId) {
            const category = this.categories.find(c => c.id === categoryId);
            return category ? category.name : 'Uncategorized';
        },
        
        /**
         * Toggle batch actions dropdown
         */
        toggleBatchActions() {
            // Implementation will be added during migration
        },
        
        /**
         * Handle batch action selection
         * @param {Event} event - Click event
         */
        handleBatchAction(event) {
            const action = event.currentTarget.getAttribute('data-action');
            
            switch (action) {
                case 'enable-all':
                    this.batchUpdateStatus(true);
                    break;
                case 'disable-all':
                    this.batchUpdateStatus(false);
                    break;
                case 'export-tools':
                    this.exportTools();
                    break;
                case 'import-tools':
                    this.importTools();
                    break;
                default:
                    break;
            }
        },
        
        /**
         * Batch update tool status
         * @param {boolean} status - New status (true = active, false = inactive)
         */
        batchUpdateStatus(status) {
            const action = status ? 'enable' : 'disable';
            
            UIModule.confirmDialog({
                title: `${action.charAt(0).toUpperCase() + action.slice(1)} All Tools`,
                message: `Are you sure you want to ${action} all tools?`,
                confirmText: 'Confirm',
                confirmButtonClass: status ? 'btn-success' : 'btn-warning'
            }).then(confirmed => {
                if (!confirmed) return;
                
                AjaxModule.put('/api/tools/batch-status', { isActive: status })
                    .then(response => {
                        OmniUtils.showFlashMessage(`All tools ${action}d successfully!`, 'success');
                        
                        // Update all tools in local array
                        this.tools.forEach(tool => {
                            tool.isActive = status;
                        });
                        
                        // Re-render tools
                        this.renderToolList();
                    })
                    .catch(error => {
                        console.error(`Error ${action}ing all tools:`, error);
                        OmniUtils.showFlashMessage(`Failed to ${action} all tools. Please try again later.`, 'error');
                    });
            });
        },
        
        /**
         * Export tools to JSON file
         */
        exportTools() {
            // Implementation will be added during migration
        },
        
        /**
         * Import tools from JSON file
         */
        importTools() {
            // Implementation will be added during migration
        }
    };
})();
