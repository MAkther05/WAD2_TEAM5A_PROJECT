document.addEventListener('DOMContentLoaded', function () {
    const sortHeaders = document.querySelectorAll('.sort-header');

    sortHeaders.forEach(header => {
        header.addEventListener('click', function () {
            const sortField = this.dataset.sort;
            const currentSort = document.getElementById('current-sort').value;
            let newSort;

            // If already sorting by this field, flip the direction
            // Otherwise, start with descending
            if (currentSort.startsWith(sortField)) {
                newSort = currentSort.includes('-desc') ?
                    currentSort.replace('-desc', '-asc') :
                    currentSort.replace('-asc', '-desc');
            } else {
                newSort = `${sortField}-desc`;
            }

            // Update sort input and trigger the AJAX reload
            document.getElementById('current-sort').value = newSort;
            updateSort(newSort);
        });
    });

    function updateSort(sortValue) {
        const tab = document.querySelector('input[name="tab"]').value;
        // Get CSRF token for safe AJAX requests
        const csrftokenInput = document.querySelector('[name=csrfmiddlewaretoken]');
        const csrftoken = csrftokenInput ? csrftokenInput.value : '';
        const reviewSection = document.querySelector('.review-scroll');

        reviewSection.innerHTML = '<div class="loading">Loading reviews...</div>';

        // AJAX fetch to get the sorted reviews (partial HTML response)
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

            const newScroll = tempDiv.querySelector('.review-scroll');
            const newPagination = tempDiv.querySelector('.pagination');

            if (newScroll) {
                // Replace the old reviews with the new sorted ones
                reviewSection.innerHTML = newScroll.innerHTML;

                // Update pagination section with the new one
                const oldPagination = document.querySelector('.pagination');
                if (oldPagination && newPagination) {
                    oldPagination.innerHTML = newPagination.innerHTML;

                    // Keep the sort parameter in pagination links
                    updatePaginationLinks(sortValue);
                }

                updateArrows(sortValue);
                // Reinitialize like buttons since they were replaced
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
            const isActive = header.dataset.sort === field;

            // If this is the current sort field, show the correct arrow
            if (isActive) {
                arrow.textContent = direction === 'desc' ? '▼' : '▲';
            } else {
                // Otherwise, clear the arrow
                arrow.textContent = '';
            }
        });
    }

    function updatePaginationLinks(sortValue) {
        const links = document.querySelectorAll('.pagination a');
        links.forEach(link => {
            // Make sure the sort stays the same when clicking to the next/prev page
            const url = new URL(link.href, window.location.origin);
            url.searchParams.set('sort', sortValue);
            // Update the actual link with the new URL
            link.href = url.toString();
        });
    }
});