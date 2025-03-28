// Function to initialize like buttons
function initializeLikeButtons() {
    document.querySelectorAll('.like-btn').forEach(button => {
        // Remove existing event listener if any
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        newButton.addEventListener('click', function() {
            const reviewId = this.getAttribute('data-review-id');
            const csrftoken = getCookie('csrftoken');

            fetch(`/ScreenCritic/review/${reviewId}/like/`, { //send POST request to like/unlike the review
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                }
            })
            .then(response => {
                if (response.status === 401) { //redirect to login page if not authenticated
                    window.location.href = `/ScreenCritic/login_register/?next=${window.location.pathname}`;
                    return;
                }
                return response.json();
            })
            .then(data => {
                if (!data) return; //stop if redirected
                document.getElementById(`like-count-${reviewId}`).textContent = data.likes; //update the like count display
                const icon = this.querySelector('i'); //get the heart icon element
                icon.classList.toggle('fa-solid', data.liked); //toggle between solid and regular heart icons based on liked state
                icon.classList.toggle('fa-regular', !data.liked);
                this.classList.toggle('liked', data.liked);
            });
        });
    });
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Initialize like buttons when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeLikeButtons();
});

// Make the initialization function available globally
window.initializeLikeButtons = initializeLikeButtons;