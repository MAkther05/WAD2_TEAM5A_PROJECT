document.addEventListener('DOMContentLoaded', function() {
    const sortHeaders = document.querySelectorAll('.sort-header');
    
    sortHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortField = this.dataset.sort;
            const currentSort = document.getElementById('current-sort').value;
            let newSort;
            
            // Toggle between asc and desc
            if (currentSort.startsWith(sortField)) {
                newSort = currentSort.includes('-desc') ? 
                    currentSort.replace('-desc', '-asc') : 
                    currentSort.replace('-asc', '-desc');
            } else {
                newSort = `${sortField}-desc`; // Default to desc
            }
            
            document.getElementById('current-sort').value = newSort;
            updateSort(newSort);
        });
    });
    
    function updateSort(sortValue) {
        const tab = document.querySelector('input[name="tab"]').value;
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const reviewSection = document.querySelector('.review-scroll');
        
        // Show loading state
        reviewSection.innerHTML = '<div class="loading">Loading reviews...</div>';
        
        fetch(`?tab=${tab}&sort=${sortValue}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': csrftoken
            }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network error');
            return response.text();
        })
        .then(html => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = html;
            const newContent = tempDiv.querySelector('.review-scroll');
            
            if (newContent) {
                reviewSection.innerHTML = newContent.innerHTML;
                updateArrows(sortValue);
                // Reinitialize like buttons
                if (typeof window.initializeLikeButtons === 'function') {
                    window.initializeLikeButtons();
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            reviewSection.innerHTML = '<div class="error">Failed to load reviews</div>';
        });
    }
    
    function updateArrows(sortValue) {
        const [field, direction] = sortValue.split('-');
        const headers = document.querySelectorAll('.sort-header');
        
        headers.forEach(header => {
            const arrow = header.querySelector('.sort-arrow');
            if (header.dataset.sort === field) {
                arrow.textContent = direction === 'desc' ? '▼' : '▲';
            } else {
                arrow.textContent = '';
            }
        });
    }
});
