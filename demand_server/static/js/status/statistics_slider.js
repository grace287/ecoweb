let slideIndex = 0;

function moveSlide(step) {
    const slides = document.querySelectorAll('.slide');
    slideIndex += step;

    if (slideIndex >= slides.length) {
        slideIndex = 0;
    } else if (slideIndex < 0) {
        slideIndex = slides.length - 1;
    }

    document.querySelector('.slider').style.transform = `translateX(-${slideIndex * 100}%)`;
}

// 자동 슬라이드 (5초 간격)
setInterval(() => moveSlide(1), 5000);
