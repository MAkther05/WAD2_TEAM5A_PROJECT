document.addEventListener("DOMContentLoaded", function() {
    const stars = document.querySelectorAll(".star-rating input");
    const starLabels = document.querySelectorAll(".star-rating .star");
    
    // Handle star hover effects
    starLabels.forEach(label => {
        label.addEventListener("mouseover", function() {
            const value = this.htmlFor.replace("star", "");
            highlightStars(value);
        });
        
        label.addEventListener("mouseout", function() {
            const checkedStar = document.querySelector(".star-rating input:checked");
            highlightStars(checkedStar ? checkedStar.value : 0);
        });
    });
    
    // Handle star selection
    stars.forEach(star => {
        star.addEventListener("change", function() {
            highlightStars(this.value);
        });
    });
    
    function highlightStars(value) {
        starLabels.forEach(label => {
            const starValue = label.htmlFor.replace("star", "");
            if (starValue <= value) {
                label.style.color = "#ffc107"; // Gold color for selected stars
            } else {
                label.style.color = "#ddd"; // Gray color for unselected stars
            }
        });
    }
});