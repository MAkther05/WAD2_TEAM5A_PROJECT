document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".notify-btn").forEach(button => {
        button.addEventListener("click", function () {
            const mediaId = this.getAttribute("data-media-id");
            const mediaTitle = this.getAttribute("data-media-title");
            const releaseDate = this.getAttribute("data-release-date");

            if (!releaseDate) {
                alert("Release date not available.");
                return;
            }

            const notificationDropdown = document.getElementById("notification-dropdown");
            const notificationItem = document.createElement("li");
            notificationItem.innerHTML = `📅 ${mediaTitle} releases on ${releaseDate}`;
            notificationDropdown.appendChild(notificationItem);

            alert(`You will be notified about ${mediaTitle}'s release on ${releaseDate}.`);
        });
    });
});