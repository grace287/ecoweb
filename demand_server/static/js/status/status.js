let currentSlide = 0; // 현재 슬라이드 인덱스
const slides = document.querySelectorAll('.statistics'); // 모든 슬라이드 선택
const totalSlides = slides.length; // 총 슬라이드 수

function changeSlide(direction) {
    slides[currentSlide].style.display = 'none'; // 현재 슬라이드 숨김
    currentSlide += direction; // 방향에 따라 슬라이드 인덱스 변경

    // 슬라이드 인덱스 범위 조정
    if (currentSlide < 0) {
        currentSlide = totalSlides - 1; // 마지막 슬라이드로 이동
    } else if (currentSlide >= totalSlides) {
        currentSlide = 0; // 첫 번째 슬라이드로 이동
    }

    slides[currentSlide].style.display = 'flex'; // 새로운 슬라이드 표시
}

// 초기 슬라이드 표시
slides[currentSlide].style.display = 'flex';
