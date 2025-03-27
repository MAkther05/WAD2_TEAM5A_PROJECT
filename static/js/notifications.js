function getMediaRoute(mediaType) {
    // Convert media type to correct route name
    switch(mediaType) {
        case "TV Show":
            return 'tv';
        case "Movie":
            return 'movies';
        case "Game":
            return 'games';
        default:
            return '';
    }
}

function markNotificationRead(subscriptionId, notificationItem) {
    fetch(`/ScreenCritic/notifications/${subscriptionId}/read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        }
    }).then(() => {
        // Add clicked class to show it's been read
        notificationItem.classList.add('clicked');
    });
}

function toggleNotifications() { //toggle notification dropdown visibility
    const dropdown = document.getElementById("notificationDropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

//close notification dropdown when clicking outside
document.addEventListener('click', function(event) {
    const bell = document.querySelector('.notification-bell');
    const dropdown = document.getElementById("notificationDropdown");
    if (!bell.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.style.display = "none";
    }
});

//fetch and display notifications when page loads
document.addEventListener('DOMContentLoaded', function() {
    fetch('/ScreenCritic/notifications/')
        .then(response => response.json())
        .then(data => {
            const notificationDropdown = document.getElementById('notificationDropdown');
            notificationDropdown.innerHTML = '';

            if (data.notifications.length > 0) {
                // Add class if more than 3 notifications
                if (data.notifications.length > 3) {
                    notificationDropdown.classList.add('has-many');
                }

                //create notification items for each notification
                data.notifications.forEach(notification => {
                    const item = document.createElement('div');
                    item.className = 'notification-item';
                    
                    // Add clicked class if already read
                    if (notification.read_by_user) {
                        item.classList.add('clicked');
                    }
                    
                    const link = document.createElement('a');
                    const mediaRoute = getMediaRoute(notification.media_type);
                    link.href = `/ScreenCritic/${mediaRoute}/${notification.media_slug}/`;
                    link.className = 'notification-link';
                    
                    // Mark notification as read when clicked
                    if (!notification.read_by_user) {
                        link.addEventListener('click', (e) => {
                            markNotificationRead(notification.subscription_id, item);
                        });
                    }

                    const imgContainer = document.createElement('div');
                    imgContainer.className = 'notification-img';
                    const img = document.createElement('img');
                    img.src = notification.cover_image;
                    img.alt = notification.media_title;
                    img.onerror = function() {
                        this.src = '/static/images/logo.png';  // Fallback image if main image fails to load
                    };
                    img.loading = 'lazy';
                    imgContainer.appendChild(img);

                    //add notification content (title, type, message)
                    const content = document.createElement('div');
                    content.className = 'notification-content';
                    content.innerHTML = `
                        <div class="notification-title">${notification.media_title}</div>
                        <div class="notification-type">${notification.media_type}</div>
                        <div class="notification-message">New Release!</div>
                        <div class="notification-date">${new Date(notification.notification_date).toLocaleDateString()}</div>
                    `;

                    //assemble notification item
                    link.appendChild(imgContainer);
                    link.appendChild(content);
                    item.appendChild(link);
                    notificationDropdown.appendChild(item);
                });
            } else {
                //show empty state message
                const emptyMessage = document.createElement('div');
                emptyMessage.className = 'notification-empty';
                emptyMessage.textContent = 'No new notifications';
                notificationDropdown.appendChild(emptyMessage);
            }
        });
});
