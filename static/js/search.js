document.addEventListener("DOMContentLoaded", function () {
    const input = document.getElementById("live-search");
    const resultsBox = document.getElementById("search-results");

    input.addEventListener("input", function () {
        const query = input.value.trim();
        if (query.length === 0) {
            resultsBox.innerHTML = "";
            resultsBox.style.display = "none";
            return;
        }

        fetch(`/ScreenCritic/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                resultsBox.innerHTML = "";

                if (data.users.length === 0 && data.media.length === 0) {
                    resultsBox.style.display = "none";
                    return;
                }

                resultsBox.style.display = "block";

                if (data.users.length > 0) {
                    const userHeader = document.createElement("div");
                    userHeader.className = "search-category";
                    userHeader.textContent = "Users";
                    resultsBox.appendChild(userHeader);

                    data.users.forEach(user => {
                        const div = document.createElement("div");
                        div.className = "search-item";
                        div.innerHTML = `<a href="/profile/${user.username}/">${user.username}</a>`;
                        resultsBox.appendChild(div);
                    });
                }

                if (data.media.length > 0) {
                    const mediaHeader = document.createElement("div");
                    mediaHeader.className = "search-category";
                    mediaHeader.textContent = "Media";
                    resultsBox.appendChild(mediaHeader);

                    data.media.forEach(media => {
                        const div = document.createElement("div");
                        div.className = "search-item";
                        div.innerHTML = `<a href="/title/${media.slug}/">${media.title} <span class="media-type">(${media.type})</span></a>`;
                        resultsBox.appendChild(div);
                    });
                }
            });
    });

    // Hide dropdown when clicking outside
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".search-wrapper")) {
            resultsBox.style.display = "none";
        }
    });
});