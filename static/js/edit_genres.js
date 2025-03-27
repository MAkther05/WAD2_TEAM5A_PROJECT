document.addEventListener("DOMContentLoaded", function () {
    //DOM elements get the html elements from their id and to use them after
    const bioTextarea = document.getElementById("bio");
    const wordCountDisplay = document.getElementById("word-count");
    const genreSelect = document.getElementById("genre-select");
    const selectedGenresContainer = document.getElementById("selected-genres");
    const selectedGenreInputs = document.getElementById("selected-genre-inputs");
    // Keep track of removed genres
    const removedGenres = new Set();

    // Create hidden input to store removed genre IDs (comma-separated)
    const removedGenresInput = document.createElement("input");
    removedGenresInput.type = "hidden";
    removedGenresInput.name = "removed_genres";
    removedGenresInput.value = "";
    selectedGenreInputs.appendChild(removedGenresInput);

    // Update word count display for the bio field
    function updateWordCount() {
        const words = bioTextarea.value.trim().split(/\s+/).filter(Boolean);
        wordCountDisplay.textContent = `${words.length} / 65 words`;
    }

    // Active listen to wordcount and update
    bioTextarea.addEventListener("input", updateWordCount);
    // Initial update on load
    updateWordCount();

    function addGenre(genreId, genreName, preloaded = false) {
        // Aviod duplicates
        if (document.querySelector(`button[data-id='${genreId}']`)) return;

        // Create genre button
        const button = document.createElement("button");
        button.type = "button";
        button.classList.add("genre-button");
        button.setAttribute("data-id", genreId);
        button.innerHTML = `${genreName} ✕`;

        // Create hidden input to submit genre with form
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "favorite_genres";
        hiddenInput.value = genreId;
        hiddenInput.setAttribute("data-id", `input-${genreId}`);

        // deletes genre when button is clicked
        button.addEventListener("click", function () {
            button.remove();
            hiddenInput.remove();
            removedGenres.add(genreId);
            removedGenresInput.value = Array.from(removedGenres).join(",");
        });

        selectedGenresContainer.appendChild(button);
        selectedGenreInputs.appendChild(hiddenInput);

        // Reset select dropdown
        if (!preloaded) {
            genreSelect.selectedIndex = 0;
        }
    }
    // When user selects a new genre from dropdown
    genreSelect.addEventListener("change", function () {
        const genreId = this.value;
        const genreName = this.options[this.selectedIndex].text;
        if (genreId) addGenre(genreId, genreName);
    });

    // Preloaded genres from template
    document.querySelectorAll("#selected-genres .genre-button").forEach(button => {
        const genreId = button.getAttribute("data-id");
        const genreName = button.textContent.replace("✕", "").trim();

        // Create hidden input for each preloaded genre
        const hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.name = "favorite_genres";
        hiddenInput.value = genreId;
        hiddenInput.setAttribute("data-id", `input-${genreId}`);
        selectedGenreInputs.appendChild(hiddenInput);

        // Add removal functionality to preloaded buttons
        button.addEventListener("click", function () {
            button.remove();
            hiddenInput.remove();
            removedGenres.add(genreId);
            removedGenresInput.value = Array.from(removedGenres).join(",");
        });
    });
});