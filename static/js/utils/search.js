/**
 * Reusable search functionality for filtering elements based on search input
 * 
 * @param {string} searchInputId - ID of the search input element
 * @param {string} containerId - ID of the container holding the items to search through
 * @param {string} itemSelector - CSS selector for individual items within the container
 * @param {string[]} searchableSelectors - Array of CSS selectors for elements within each item to search through
 * @param {Object} [options] - Additional options
 * @param {string} [options.counterElementId] - ID of the element to display the item count
 * @param {number} [options.itemsPerPage] - Number of items to show per page (0 for no pagination)
 * @param {string} [options.paginationContainerId] - ID of the pagination controls container
 */
export function initializeSearch(searchInputId, containerId, itemSelector, searchableSelectors, options = {}) {
    const {
        counterElementId = null,
        itemsPerPage = 0,
        paginationContainerId = null
    } = options;

    const searchInput = document.getElementById(searchInputId);
    if (!searchInput) return;

    const container = document.getElementById(containerId);
    if (!container) return;

    let currentPage = 1;
    let totalItems = 0;
    let totalPages = 1;

    // Initialize counter element if provided
    const counterElement = counterElementId ? document.getElementById(counterElementId) : null;
    
    // Initialize pagination if enabled
    let paginationContainer = null;
    if (itemsPerPage > 0 && paginationContainerId) {
        paginationContainer = document.getElementById(paginationContainerId);
        if (paginationContainer) {
            paginationContainer.addEventListener('click', handlePaginationClick);
        }
    }

    // Initial search
    performSearch();

    // Set up input event listener
    searchInput.addEventListener('input', () => {
        currentPage = 1; // Reset to first page on new search
        performSearch();
    });

    function updateCounter(visibleCount) {
        if (counterElement) {
            if (itemsPerPage > 0) {
                const start = ((currentPage - 1) * itemsPerPage) + 1;
                const end = Math.min(start + itemsPerPage - 1, visibleCount);
                counterElement.textContent = `Showing ${start}-${end} of ${visibleCount} items`;
            } else {
                counterElement.textContent = `Found ${visibleCount} items`;
            }
        }
    }

    function updatePagination(visibleCount) {
        if (!paginationContainer) return;
        
        totalItems = visibleCount;
        totalPages = itemsPerPage > 0 ? Math.ceil(visibleCount / itemsPerPage) : 1;
        
        let paginationHTML = '';
        if (totalPages > 1) {
            paginationHTML = `
                <button class="page-btn" data-page="first" ${currentPage === 1 ? 'disabled' : ''}>«</button>
                <button class="page-btn" data-page="prev" ${currentPage === 1 ? 'disabled' : ''}>‹</button>
                <span class="page-info">Page ${currentPage} of ${totalPages}</span>
                <button class="page-btn" data-page="next" ${currentPage >= totalPages ? 'disabled' : ''}>›</button>
                <button class="page-btn" data-page="last" ${currentPage >= totalPages ? 'disabled' : ''}>»</button>
            `;
        }
        
        paginationContainer.innerHTML = paginationHTML;
    }

    function handlePaginationClick(event) {
        const target = event.target.closest('.page-btn');
        if (!target) return;

        const action = target.dataset.page;
        
        switch (action) {
            case 'first':
                if (currentPage > 1) {
                    currentPage = 1;
                    performSearch();
                }
                break;
            case 'prev':
                if (currentPage > 1) {
                    currentPage--;
                    performSearch();
                }
                break;
            case 'next':
                if (currentPage < totalPages) {
                    currentPage++;
                    performSearch();
                }
                break;
            case 'last':
                if (currentPage < totalPages) {
                    currentPage = totalPages;
                    performSearch();
                }
                break;
        }
    }

    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase().trim();
        const allItems = Array.from(container.querySelectorAll(itemSelector));
        let visibleItems = [];

        // Filter items based on search
        visibleItems = allItems.filter(item => {
            if (searchTerm === '') return true;
            
            return searchableSelectors.some(selector => {
                const element = item.querySelector(selector);
                return element && element.textContent.toLowerCase().includes(searchTerm);
            });
        });

        // Update visibility of all items
        allItems.forEach((item, index) => {
            const isVisible = visibleItems.includes(item);
            item.style.display = isVisible ? '' : 'none';
            
            // Apply pagination if enabled
            if (isVisible && itemsPerPage > 0) {
                const itemIndex = visibleItems.indexOf(item);
                const startIndex = (currentPage - 1) * itemsPerPage;
                const endIndex = startIndex + itemsPerPage;
                item.style.display = (itemIndex >= startIndex && itemIndex < endIndex) ? '' : 'none';
            }
        });

        // Update counter and pagination
        updateCounter(visibleItems.length);
        updatePagination(visibleItems.length);
    }
}
