class SlideManager {
    constructor() {
        this.slides = document.querySelectorAll('.slide');
        this.currentSlide = 1;
        this.totalSlides = this.slides.length;
        this.currentElement = document.querySelector('.current');
        this.totalElement = document.querySelector('.total');
        this.prevBtn = document.querySelector('.nav-btn.prev');
        this.nextBtn = document.querySelector('.nav-btn.next');
        
        this.initialize();
    }

    initialize() {
        this.updatePagination();
        this.bindEvents();
        this.showSlide(this.currentSlide);
    }

    updatePagination() {
        this.currentElement.textContent = this.currentSlide;
        this.totalElement.textContent = this.totalSlides;
    }

    showSlide(number) {
        this.slides.forEach(slide => slide.classList.remove('active'));
        this.slides[number - 1].classList.add('active');
        this.currentSlide = number;
        this.updatePagination();
    }

    nextSlide() {
        if (this.currentSlide < this.totalSlides) {
            this.showSlide(this.currentSlide + 1);
        }
    }

    prevSlide() {
        if (this.currentSlide > 1) {
            this.showSlide(this.currentSlide - 1);
        }
    }

    bindEvents() {
        this.nextBtn.addEventListener('click', () => this.nextSlide());
        this.prevBtn.addEventListener('click', () => this.prevSlide());

        // 키보드 접근성
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowRight') {
                this.nextSlide();
            } else if (e.key === 'ArrowLeft') {
                this.prevSlide();
            }
        });
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    new SlideManager();
});