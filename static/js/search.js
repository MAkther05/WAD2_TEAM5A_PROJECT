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

                // Users section
                if (data.users.length > 0) {
                    const userHeader = document.createElement("div");
                    userHeader.className = "search-category";
                    userHeader.textContent = "Users";
                    resultsBox.appendChild(userHeader);

                    data.users.forEach(user => {
                        const div = document.createElement("div");
                        div.className = "search-item";

                        const profilePic = user.profile_picture;  // use as-is

                        div.innerHTML = `
                            <a href="/ScreenCritic/profile/${user.username}/">
                                <img src="${profilePic}" class="search-thumb user-thumb" alt="${user.username}'s Profile Picture" />
                                <span>${user.username}</span>
                            </a>
                        `;
                        resultsBox.appendChild(div);
                    });
                }

                // Media section
                if (data.media.length > 0) {
                    const mediaHeader = document.createElement("div");
                    mediaHeader.className = "search-category";
                    mediaHeader.textContent = "Media";
                    resultsBox.appendChild(mediaHeader);

                    data.media.forEach(media => {
                        const type = media.type.toLowerCase();
                        let path = "";
                        if (type === "tv show") path = "tv";
                        else if (type === "movie") path = "movies";
                        else if (type === "game") path = "games";

                        const cover = media.cover_image;  // use as-is

                        const div = document.createElement("div");
                        div.className = "search-item";
                        div.innerHTML = `
                            <a href="/ScreenCritic/${path}/${media.slug}/">
                                <img src="${cover}" class="search-thumb media-thumb" alt="${media.title} Cover" />
                                <span>${media.title} <span class="media-type">(${media.type})</span></span>
                            </a>
                        `;
                        resultsBox.appendChild(div);
                    });
                }
            });
    });

    // Hide popup when clicking outside
    document.addEventListener("click", function (e) {
        if (!e.target.closest(".search-wrapper")) {
            resultsBox.style.display = "none";
        }
    });
});