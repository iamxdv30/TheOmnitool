document.addEventListener('DOMContentLoaded', function() {
    // Event listener for showing/hiding the update form
    document.querySelectorAll('.showUpdateForm').forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('.user-row');
            const updateForm = userRow.nextElementSibling;
            if (updateForm && updateForm.classList.contains('update-form')) {
                // Hide all other forms before showing the new one
                document.querySelectorAll('.update-form, .tool-access, .change-role').forEach(form => {
                    if (form !== updateForm) {
                        form.style.display = 'none';
                    }
                });
                updateForm.style.display = updateForm.style.display === 'none' ? 'table-row' : 'none';
            }
        });
    });

    // Event listener for showing/hiding the tool access form
    document.querySelectorAll('.showToolAccess').forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('.user-row');
            const toolAccessForm = userRow.nextElementSibling.nextElementSibling;
            if (toolAccessForm && toolAccessForm.classList.contains('tool-access')) {
                // Hide all other forms before showing the new one
                document.querySelectorAll('.update-form, .tool-access, .change-role').forEach(form => {
                    if (form !== toolAccessForm) {
                        form.style.display = 'none';
                    }
                });
                toolAccessForm.style.display = toolAccessForm.style.display === 'none' ? 'table-row' : 'none';
            }
        });
    });

    // Event listener for showing/hiding the change role form
    document.querySelectorAll('.showChangeRole').forEach(button => {
        button.addEventListener('click', function() {
            const userRow = this.closest('.user-row');
            const changeRoleForm = userRow.nextElementSibling.nextElementSibling.nextElementSibling;
            if (changeRoleForm && changeRoleForm.classList.contains('change-role')) {
                // Hide all other forms before showing the new one
                document.querySelectorAll('.update-form, .tool-access, .change-role').forEach(form => {
                    if (form !== changeRoleForm) {
                        form.style.display = 'none';
                    }
                });
                changeRoleForm.style.display = changeRoleForm.style.display === 'none' ? 'table-row' : 'none';
            }
        });
    });

    // Confirmation for delete user form
    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to delete this user?')) {
                e.preventDefault();
            }
        });
    });
});
