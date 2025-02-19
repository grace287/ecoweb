// chat_estimate.js
document.addEventListener('DOMContentLoaded', function() {
    const chatFlow = {
        currentStep: 1,
        data: {
            serviceType: '',
            location: '',
            date: ''
        },

        init() {
            this.bindEvents();
            this.showStep(1);
        },

        bindEvents() {
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.data.serviceType = e.target.dataset.value;
                    this.nextStep();
                });
            });

            document.querySelectorAll('.submit-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const input = e.target.closest('.chat-content').querySelector('input');
                    if (input && input.value.trim()) {
                        if (this.currentStep === 2) {
                            this.data.location = input.value;
                        }
                        this.nextStep();
                    }
                });
            });

            document.querySelectorAll('.date-option').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.date-option').forEach(b => b.classList.remove('selected'));
                    e.target.classList.add('selected');
                    this.data.date = e.target.textContent;
                });
            });

            document.querySelector('.request-btn')?.addEventListener('click', () => {
                this.submitRequest();
            });
        },

        showStep(step) {
            document.querySelectorAll('.chat-box').forEach(box => {
                box.style.display = box.dataset.step == step ? 'block' : 'none';
            });
            this.currentStep = step;
        },

        nextStep() {
            this.showStep(this.currentStep + 1);
        },

        updateSummary() {
            // 요약 정보 업데이트
            const summary = document.querySelector('.summary');
            if (summary) {
                summary.querySelector('[data-type="service"]').textContent = this.data.serviceType;
                summary.querySelector('[data-type="location"]').textContent = this.data.location;
                summary.querySelector('[data-type="date"]').textContent = this.data.date;
            }
        },

        async submitRequest() {
            try {
                const response = await fetch('/api/estimates/create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken')
                    },
                    body: JSON.stringify(this.data)
                });

                if (response.ok) {
                    const data = await response.json();
                    console.log('견적 요청 성공:', data);
                    
                    // 회원가입 안내 섹션 표시
                    document.querySelector('[data-step="5"]').style.display = 'block';
                    
                    // 견적 요청 버튼 비활성화
                    document.querySelector('.request-btn').disabled = true;
                    document.querySelector('.request-btn').textContent = '견적 요청 완료';
                } else {
                    throw new Error('견적 요청 실패');
                }
            } catch (error) {
                console.error('견적 요청 오류:', error);
                alert('견적 요청 중 오류가 발생했습니다. 다시 시도해주세요.');
            }
        }
    };

    chatFlow.init();

    // CSRF 토큰 가져오기
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});


// chat_estimate.js에 추가
function showSignupGuide() {
    const signupGuide = document.querySelector('.signup-guide');
    if (signupGuide) {
        signupGuide.style.display = 'block';
        
        // 스크롤을 회원가입 안내 섹션으로 부드럽게 이동
        signupGuide.scrollIntoView({ behavior: 'smooth' });
    }
}

// 견적 요청 버튼 클릭 시 회원가입 안내 표시
document.querySelector('.request-btn').addEventListener('click', (e) => {
    e.preventDefault();
    showSignupGuide();
});

// 소셜 로그인 버튼 이벤트 핸들러
document.querySelectorAll('.signup-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const signupType = e.currentTarget.classList[1]; // email, kakao, naver, payco
        
        switch(signupType) {
            case 'email':
                window.location.href = '/accounts/signup/';
                break;
            case 'kakao':
                window.location.href = '/accounts/kakao/login/';
                break;
            case 'naver':
                window.location.href = '/accounts/naver/login/';
                break;
            case 'payco':
                window.location.href = '/accounts/payco/login/';
                break;
        }
    });
});