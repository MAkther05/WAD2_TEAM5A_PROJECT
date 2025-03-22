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
