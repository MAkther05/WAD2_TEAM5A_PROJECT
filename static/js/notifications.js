function toggleNotifications() {
    const dropdown = document.getElementById("notificationDropdown");
    dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
}

document.addEventListener('click', function(event) {
    const bell = document.querySelector('.notification-bell');
    const dropdown = document.getElementById("notificationDropdown");
    if (!bell.contains(event.target) && !dropdown.contains(event.target)) {
        dropdown.style.display = "none";
    }
});


document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".notify-btn").forEach(button => {
        button.addEventListener("click", function () {
            const mediaTitle = this.closest(".upcoming-item").querySelector("h3").textContent;
            const releaseDate = this.closest(".upcoming-item").querySelector("strong").nextSibling.nodeValue.trim();

            if (!releaseDate) {
                alert("Release date not available.");
                return;
            }

            const notificationDropdown = document.getElementById("notificationDropdown");
            const notificationList = notificationDropdown.querySelector("ul");

            // Check for duplicate notifications
            if ([...notificationList.children].some(item => item.textContent.includes(mediaTitle))) {
                alert(`You're already subscribed to ${mediaTitle}'s release notification.`);
                return;
            }

            // Create a new notification item
            const notificationItem = document.createElement("li");
            notificationItem.innerHTML = `📅 ${mediaTitle} releases on ${releaseDate}`;
            notificationList.appendChild(notificationItem);

            alert(`You will be notified about ${mediaTitle}'s release on ${releaseDate}.`);
        });
    });
});
