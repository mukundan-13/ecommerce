document.addEventListener('DOMContentLoaded', function() {
    // Image slider functionality
    const sliderImages = document.querySelectorAll('.img-slider .img');
    let currentIndex = 0;

    function showSlide(index) {
        sliderImages.forEach((img, i) => {
            img.style.transform = `translateX(${-100 * index}%)`;
        });
    }

    function nextSlide() {
        currentIndex = (currentIndex + 1) % sliderImages.length;
        showSlide(currentIndex);
    }

    function prevSlide() {
        currentIndex = (currentIndex - 1 + sliderImages.length) % sliderImages.length;
        showSlide(currentIndex);
    }

    setInterval(nextSlide, 3000); // Change slide every 3 seconds

    // Menu toggle functionality for mobile
    const menuToggle = document.querySelector('.heading1 ion-icon');
    const menu = document.querySelector('.menu');

    menuToggle.addEventListener('click', () => {
        menu.classList.toggle('show');
    });

    const closeMenu = document.querySelector('.menu .close');
    closeMenu.addEventListener('click', () => {
        menu.classList.remove('show');
    });
});
