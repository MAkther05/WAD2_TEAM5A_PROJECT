document.addEventListener("DOMContentLoaded", function () {
    const notifyButtons = document.querySelectorAll(".notify-btn");

    notifyButtons.forEach(button => {
        button.addEventListener("click", function () {
            const mediaId = this.getAttribute("data-media-id");

            fetch(`/toggle-notification/${mediaId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/json"
                },
                credentials: "include"
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "added") {
                    alert("Notification set! You’ll be notified on release.");
                    this.textContent = "🔔✔";
                } else {
                    alert("Notification removed.");
                    this.textContent = "🔔";
                }
            });
        });
    });

    function getCSRFToken() {
        return document.querySelector("[name=csrfmiddlewaretoken]").value;
    }
});
