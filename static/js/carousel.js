const track = document.getElementById('topReviewsTrack');
const items = document.querySelectorAll('.carousel-item');
let currentIndex = 0;

const updateActive = () => {
    items.forEach((item, index) => {
        item.classList.toggle('active', index === currentIndex);
    });
    const offsetLeft = items[currentIndex].offsetLeft;
    const containerCenter = track.offsetWidth / 2 - items[currentIndex].offsetWidth / 2;
    track.scrollTo({ left: offsetLeft - containerCenter, behavior: 'smooth' });
};

document.getElementById('nextBtn').addEventListener('click', () => {
    currentIndex = (currentIndex + 1) % items.length;
    updateActive();
});

document.getElementById('prevBtn').addEventListener('click', () => {
    currentIndex = (currentIndex - 1 + items.length) % items.length;
    updateActive();
});

// Auto-scroll every 5 seconds
setInterval(() => {
    currentIndex = (currentIndex + 1) % items.length;
    updateActive();
}, 5000);

// Center on load
window.addEventListener('load', updateActive); 