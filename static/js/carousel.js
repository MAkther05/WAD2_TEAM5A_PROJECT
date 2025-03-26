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

    function updateCarousel() {
        const itemWidth = items[index].offsetWidth;
        const containerWidth = document.querySelector(".carousel-container").offsetWidth;

        // Calculate offset to keep active item centered
        const offset = (containerWidth / 2) - (itemWidth / 2) - (index * itemWidth);

        track.style.transform = `translateX(${offset}px)`;

        // Update item styles
        items.forEach((item, i) => {
            if (i === index) {
                item.classList.add("active");
                item.style.transform = "scale(1)";
                item.style.opacity = "1";
            } else {
                item.classList.remove("active");
                item.style.transform = "scale(0.8)";
                item.style.opacity = "0.5";
            }
        });
        // items.forEach((item, i) => {
        //     if (i === index) {
        //         item.classList.add("active");
        //     } else {
        //         item.classList.remove("active");
        //     }
        // });

        // const offset = items[index].offsetWidth * -index;
        // track.style.transform = `translateX(${offset}px)`;
    }

    nextButton.addEventListener("click", () => {
        index = (index + 1) % items.length;
        updateCarousel();
    });

    prevButton.addEventListener("click", () => {
        index = (index - 1 + items.length) % items.length;
        updateCarousel();
    });

    updateCarousel();
});
