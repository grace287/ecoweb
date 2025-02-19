// static/js/system_intro.js
class SlideManager {
    constructor() {
        this.slides = document.querySelectorAll('.slide');
        this.dots = document.querySelectorAll('.dot');
        this.currentSlide = 0;
        this.slideInterval = null;
        this.initializeSlider();
    }

    initializeSlider() {
        this.showSlide(this.currentSlide);
        this.startSlideshow();
        this.bindEvents();
    }

    showSlide(index) {
        this.slides.forEach(slide => slide.classList.remove('active'));
        this.dots.forEach(dot => dot.classList.remove('active'));
        
        this.slides[index].classList.add('active');
        this.dots[index].classList.add('active');
    }

    nextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.slides.length;
        this.showSlide(this.currentSlide);
    }

    startSlideshow() {
        this.slideInterval = setInterval(() => this.nextSlide(), 5000);
    }

    stopSlideshow() {
        clearInterval(this.slideInterval);
    }

    bindEvents() {
        // 도트 클릭 이벤트
        this.dots.forEach((dot, index) => {
            dot.addEventListener('click', () => {
                this.currentSlide = index;
                this.showSlide(this.currentSlide);
                this.stopSlideshow();
                this.startSlideshow();
            });
        });

        // 슬라이더 호버 이벤트
        const sliderContainer = document.querySelector('.slider-container');
        sliderContainer.addEventListener('mouseenter', () => this.stopSlideshow());
        sliderContainer.addEventListener('mouseleave', () => this.startSlideshow());
    }
}

class ScrollManager {
    constructor() {
        this.scrollButtons = document.querySelectorAll('.scroll-to-top');
        this.initializeScroll();
    }

    initializeScroll() {
        this.bindScrollEvents();
        this.checkScrollPositions();
    }

    scrollToTop() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    }

    scrollToSection(targetId) {
        const targetSection = document.getElementById(targetId);
        if (!targetSection) return;

        const headerOffset = 80;
        const elementPosition = targetSection.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }

    checkScrollPositions() {
        this.scrollButtons.forEach(button => {
            const section = button.closest('section');
            if (section) {
                const sectionTop = section.offsetTop;
                const sectionBottom = sectionTop + section.offsetHeight;
                const scrollPosition = window.pageYOffset;
                
                button.style.opacity = (scrollPosition >= sectionTop && 
                    scrollPosition < sectionBottom) ? '1' : '0';
                button.style.visibility = (scrollPosition >= sectionTop && 
                    scrollPosition < sectionBottom) ? 'visible' : 'hidden';
            }
        });
    }

    bindScrollEvents() {
        // 스크롤 버튼 이벤트
        this.scrollButtons.forEach(button => {
            button.addEventListener('click', () => this.scrollToTop());
        });

        // CTA 버튼 이벤트
        document.querySelectorAll('.cta-button[data-target]').forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.scrollToSection(button.getAttribute('data-target'));
            });
        });

        // 스크롤 이벤트
        window.addEventListener('scroll', () => {
            requestAnimationFrame(() => this.checkScrollPositions());
        });
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    // 페이지 로드 시 맨 위로 스크롤
    window.onbeforeunload = () => window.scrollTo(0, 0);

    new SlideManager();
    new ScrollManager();
});