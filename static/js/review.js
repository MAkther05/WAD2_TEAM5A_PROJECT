document.addEventListener("DOMContentLoaded", function () {
    const stars = document.querySelectorAll(".star-rating input");
    
    stars.forEach(star => {
        star.addEventListener("change", function () {
            updateStars(this.value);
        });
    });

    function updateStars(value) {
        stars.forEach(star => {
            if (star.value <= value) {
                star.nextElementSibling.style.color = "gold";
            } else {
                star.nextElementSibling.style.color = "gray";
            }
        });
    }
});