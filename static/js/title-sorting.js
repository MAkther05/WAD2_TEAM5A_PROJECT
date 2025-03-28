document.addEventListener('DOMContentLoaded', function() {
    const sortHeaders = document.querySelectorAll('.sort-header');
    const currentSortInput = document.getElementById('current-sort');
    
    sortHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const sortField = this.dataset.sort;
            const currentSort = currentSortInput.value;
            const [currentField, currentDirection] = currentSort.split('-');
            
            let newDirection = 'desc';
            if (sortField === currentField && currentDirection === 'desc') {
                newDirection = 'asc';
            }
            
            const newSort = `${sortField}-${newDirection}`;
            currentSortInput.value = newSort;
            
            // Update arrow indicators
            sortHeaders.forEach(h => {
                const arrow = h.querySelector('.sort-arrow');
                if (h === this) {
                    arrow.textContent = newDirection === 'desc' ? '▼' : '▲';
                } else {
                    arrow.textContent = '';
                }
            });
            
            // Get CSRF token
            const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            
            // Make AJAX request to update reviews
            const url = new URL(window.location.href);
            url.searchParams.set('sort', newSort);
            
            fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': csrftoken
                }
            })
            .then(response => response.text())
            .then(html => {
                const parser = new DOMParser();
                const doc = parser.parseFromString(html, 'text/html');
                const newReviews = doc.querySelector('.reviews-scroll');
                if (newReviews) {
                    document.querySelector('.reviews-scroll').innerHTML = newReviews.innerHTML;
                    
                    // Reinitialize like buttons
                    if (typeof window.initializeLikeButtons === 'function') {
                        window.initializeLikeButtons();
                    }
                }
            })
            .catch(error => console.error('Error:', error));
            
            // Update URL without page reload
            window.history.pushState({}, '', url);
        });
    });
}); 