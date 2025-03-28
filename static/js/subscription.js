document.addEventListener('DOMContentLoaded', function() {
    const notificationButtons = document.querySelectorAll('.notification-btn');
    console.log('Found notification buttons:', notificationButtons.length);
    
    notificationButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Try different ways to get the media ID
            const mediaId = this.getAttribute('data-media-id') || this.dataset.mediaId;
            console.log('Button element:', this);
            console.log('All data attributes:', this.dataset);
            console.log('Direct attribute:', this.getAttribute('data-media-id'));
            console.log('Clicked notification button for media ID:', mediaId);
            
            if (!mediaId) {
                console.error('No media ID found on button');
                showMessage('Invalid media ID', 'error');
                return;
            }

            const csrftoken = getCookie('csrftoken');
            
            // Construct the URL
            const url = `/ScreenCritic/toggle-subscription/${mediaId}/`;
            console.log('Fetching URL:', url);
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                credentials: 'same-origin'
            })
            .then(response => {
                console.log('Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('Response data:', data);
                if (data.status === 'success') {
                    // Update icon appearance
                    const icon = this.querySelector('i');
                    if (data.is_subscribed) {
                        this.classList.add('subscribed');
                        icon.classList.remove('fa-regular');
                        icon.classList.add('fa-solid');
                    } else {
                        this.classList.remove('subscribed');
                        icon.classList.remove('fa-solid');
                        icon.classList.add('fa-regular');
                    }
                    
                    // Show success message
                    const message = data.is_subscribed ? 'You will be notified when this is released' : 'Notification removed';
                    showMessage(message, 'success');
                } else {
                    showMessage(data.message || 'An error occurred', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showMessage('An error occurred while processing your request', 'error');
            });
        });
    });
});

// Helper function to get CSRF token
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

function showMessage(message, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);

    // Automatically remove the message after fadeOut ends
    messageDiv.addEventListener('animationend', (e) => {
        if (e.animationName === 'fadeOut') {
            messageDiv.remove();
        }
    });
}