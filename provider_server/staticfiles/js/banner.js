// banner.js
let currentSlide = 0; // 현재 슬라이드 인덱스
const slides = document.querySelectorAll('.slide'); // 모든 슬라이드 선택
const totalSlides = slides.length; // 총 슬라이드 수

function changeSlide(direction) {
    slides[currentSlide].classList.remove('active'); // 현재 슬라이드 숨김
    currentSlide += direction; // 방향에 따라 슬라이드 인덱스 변경

    // 슬라이드 인덱스 범위 조정
    if (currentSlide < 0) {
        currentSlide = totalSlides - 1; // 마지막 슬라이드로 이동
    } else if (currentSlide >= totalSlides) {
        currentSlide = 0; // 첫 번째 슬라이드로 이동
    }

    slides[currentSlide].classList.add('active'); // 새로운 슬라이드 표시
    updateSlide(); // 슬라이드 번호 업데이트
}

function updateSlide() {
    const slideNumber = document.querySelector('.slide-number');
    slideNumber.textContent = `${currentSlide + 1} / ${totalSlides}`; // 현재 슬라이드 번호 업데이트
}

// 초기 슬라이드 업데이트
updateSlide();