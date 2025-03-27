// document.addEventListener("DOMContentLoaded", function () {
//     let currentIndex = 0;
//     const slides = document.querySelectorAll(".carousel-item");
//     const totalSlides = slides.length;
//     const track = document.querySelector(".carousel-track");

//     function updateSlides() {
//         slides.forEach((slide, index) => {
//             slide.classList.remove("active");

//             if (index === currentIndex) {
//                 slide.classList.add("active");
//             }
//         });

//         // Adjust the transform property to center active item
//         const offset = -currentIndex * 65; // Adjust for spacing
//         track.style.transform = `translateX(${offset}%)`;
//     }

//     function moveSlide(direction) {
//         currentIndex += direction;

//         if (currentIndex >= totalSlides) {
//             currentIndex = 0;
//         } else if (currentIndex < 0) {
//             currentIndex = totalSlides - 1;
//         }

//         updateSlides();
//     }

//     document.querySelector(".prev").addEventListener("click", function () {
//         moveSlide(-1);
//     });

//     document.querySelector(".next").addEventListener("click", function () {
//         moveSlide(1);
//     });

//     updateSlides();
// });


document.addEventListener("DOMContentLoaded", function () {
    const track = document.querySelector(".carousel-track");
    const items = Array.from(track.children);
    const prevButton = document.querySelector(".prev");
    const nextButton = document.querySelector(".next");

    let index = 0;
    const itemWidth = 540; // 500px width + 40px gap

    function updateCarousel() {
        // Calculate the offset to move the track
        const offset = -index * itemWidth;
        track.style.transform = `translateX(${offset}px)`;
    }

    nextButton.addEventListener("click", () => {
        index = (index + 1) % items.length; // Loop back to start when reaching end
        updateCarousel();
    });

    prevButton.addEventListener("click", () => {
        index = (index - 1 + items.length) % items.length; // Loop to end when going back from start
        updateCarousel();
    });

    // Initialize carousel
    updateCarousel();
});
