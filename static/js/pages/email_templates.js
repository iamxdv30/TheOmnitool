document.addEventListener('DOMContentLoaded', () => {
    const addTemplateForm = document.getElementById('addTemplateForm');
    const templateList = document.getElementById('templateList');
        const errorMessages = document.getElementById('errorMessages');
    const searchInput = document.getElementById('searchInput');

    // Add a new template
    addTemplateForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        const formData = new FormData(addTemplateForm);
        const title = formData.get('title');
        const content = formData.get('content');

        try {
            const response = await fetch('/tools/email_templates', {
                method: 'POST',
                body: new URLSearchParams({ title, content }),
            });

            if (response.ok) {
                window.location.reload();
            } else {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    errorMessages.textContent = errorData.error || 'Failed to add template.';
                } else {
                    errorMessages.textContent = 'Failed to add template. The server returned an unexpected response.';
                }
            }
        } catch (error) {
            errorMessages.textContent = 'An error occurred: ' + error.message;
        }
    });

    // Search functionality
    searchInput.addEventListener('input', () => {
        const searchTerm = searchInput.value.toLowerCase();
        const templates = templateList.querySelectorAll('.template');

        templates.forEach(template => {
            const title = template.querySelector('.template-title').textContent.toLowerCase();
            const content = template.querySelector('.template-content').textContent.toLowerCase();
            const isVisible = title.includes(searchTerm) || content.includes(searchTerm);
            template.style.display = isVisible ? '' : 'none';
        });
    });

    // Delegate events for template actions
    templateList.addEventListener('click', async (event) => {
        const target = event.target;
        const templateDiv = target.closest('.template');
        if (!templateDiv) return;

        const templateId = templateDiv.dataset.id;

        // Delete
        if (target.classList.contains('delete-btn')) {
            if (confirm('Are you sure you want to delete this template?')) {
                try {
                    const response = await fetch(`/tools/email_templates/${templateId}`, {
                        method: 'DELETE',
                    });
                    if (response.ok) {
                        templateDiv.remove();
                    } else {
                        const errorData = await response.json();
                        alert('Failed to delete template: ' + (errorData.error || 'Unknown error'));
                    }
                } catch (err) {
                    alert('An error occurred: ' + err.message);
                }
            }
        }

        // Copy
        if (target.classList.contains('copy-btn')) {
            const content = templateDiv.querySelector('.template-content').textContent;
            navigator.clipboard.writeText(content).then(() => {
                alert('Template content copied to clipboard!');
            }, (err) => {
                alert('Failed to copy: ' + err);
            });
        }

        // Update (make fields editable)
        if (target.classList.contains('update-btn')) {
            const titleDiv = templateDiv.querySelector('.template-title');
            const contentDiv = templateDiv.querySelector('.template-content');

            // Make title editable
            titleDiv.contentEditable = true;
            titleDiv.dataset.original = titleDiv.textContent;

            // Replace content div with a textarea
            const content = contentDiv.textContent;
            const textarea = document.createElement('textarea');
            textarea.className = 'editing-textarea';
            textarea.value = content;
            contentDiv.style.display = 'none'; // Hide the original content div
            contentDiv.parentNode.insertBefore(textarea, contentDiv.nextSibling);

            titleDiv.focus();
            templateDiv.classList.add('editing');
        }

        // Cancel update
        if (target.classList.contains('cancel-btn')) {
            const titleDiv = templateDiv.querySelector('.template-title');
            const contentDiv = templateDiv.querySelector('.template-content');

            // Restore title
            titleDiv.textContent = titleDiv.dataset.original;
            titleDiv.contentEditable = false;

            // Remove textarea and show original content div
            const textarea = templateDiv.querySelector('.editing-textarea');
            if (textarea) {
                textarea.remove();
            }
            contentDiv.style.display = '';

            templateDiv.classList.remove('editing');
        }

        // Save update
        if (target.classList.contains('save-btn')) {
            const titleDiv = templateDiv.querySelector('.template-title');
            const contentDiv = templateDiv.querySelector('.template-content');
            const textarea = templateDiv.querySelector('.editing-textarea');

            const newTitle = titleDiv.textContent;
            const newContent = textarea.value;

            try {
                const response = await fetch(`/tools/email_templates/${templateId}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ title: newTitle, content: newContent }),
                });

                if (response.ok) {
                    titleDiv.contentEditable = false;
                    
                    contentDiv.textContent = newContent;
                    textarea.remove();
                    contentDiv.style.display = '';
                    templateDiv.classList.remove('editing');
                    alert('Template updated successfully!');
                } else {
                    const errorData = await response.json();
                    alert('Failed to update template: ' + (errorData.error || 'Unknown error'));
                }
            } catch (err) {
                console.error('Save error:', err);
                alert('An unexpected error occurred. Please check the console for details.');
            }
        }
    });
});
