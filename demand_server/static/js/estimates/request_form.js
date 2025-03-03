
    document.addEventListener('DOMContentLoaded', function() {
    const chatFlow = {
        data: {
            service_type: '',
            measurement_location: '',
            preferred_schedule: '',
            address: '',
            contact_name: '',
            contact_phone: '',
            contact_email: ''
        },

        init() {
            this.bindEvents();
        },

        bindEvents() {
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.data.service_type = e.target.dataset.value;
                    this.updateSummary();
                });
            });

            document.querySelector('.request-btn')?.addEventListener('click', (e) => {
                e.preventDefault();
                this.submitRequest();
            });
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
                    const result = await response.json();
                    console.log('견적 요청 성공:', result);
                    
                    // 견적번호 표시 및 회원가입 안내
                    document.querySelector('.estimate-number').textContent = result.estimate_number;
                    showSignupGuide();
                    
                    // 견적 요청 버튼 비활성화
                    document.querySelector('.request-btn').disabled = true;
                    document.querySelector('.request-btn').textContent = '견적 요청 완료';
                } else {
                    const error = await response.json();
                    throw new Error(error.error || '견적 요청 실패');
                }
            } catch (error) {
                console.error('견적 요청 오류:', error);
                alert(error.message || '견적 요청 중 오류가 발생했습니다. 다시 시도해주세요.');
            }
        }
    };

    chatFlow.init();

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

document.addEventListener('DOMContentLoaded', function() {
    const chatFlow = {
        data: {
            service_type: '',
            measurement_location: '',
            preferred_schedule: '',
            address: '',
            contact_name: '',
            contact_phone: '',
            contact_email: ''
        },

        init() {
            this.bindEvents();
        },

        bindEvents() {
            document.querySelectorAll('.option-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    this.data.service_type = e.target.dataset.value;
                    this.updateSummary();
                });
            });

            document.querySelectorAll('.submit-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const input = e.target.closest('.chat-content').querySelector('input');
                    if (input && input.value.trim()) {
                        if (input.classList.contains('chat-input')) {
                            this.data.address = input.value;
                        }
                        this.updateSummary();
                    }
                });
            });

            document.querySelectorAll('.date-option').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    document.querySelectorAll('.date-option').forEach(b => b.classList.remove('selected'));
                    e.target.classList.add('selected');
                    this.data.preferred_schedule = e.target.textContent;
                    this.updateSummary();
                });
            });

            document.querySelector('.request-btn')?.addEventListener('click', () => {
                this.submitRequest();
            });
        },

        updateSummary() {
            document.querySelector('[data-type="service"]').textContent = this.data.service_type;
            document.querySelector('[data-type="location"]').textContent = this.data.measurement_location;
            document.querySelector('[data-type="date"]').textContent = this.data.preferred_schedule;
            document.querySelector('[data-type="address"]').textContent = this.data.address;
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
                    const result = await response.json();
                    console.log('견적 요청 성공:', result);
                    
                    // 견적번호 표시 및 회원가입 안내
                    document.querySelector('.estimate-number').textContent = result.estimate_number;
                    showSignupGuide();
                    
                    // 견적 요청 버튼 비활성화
                    document.querySelector('.request-btn').disabled = true;
                    document.querySelector('.request-btn').textContent = '견적 요청 완료';
                } else {
                    const error = await response.json();
                    throw new Error(error.error || '견적 요청 실패');
                }
            } catch (error) {
                console.error('견적 요청 오류:', error);
                alert(error.message || '견적 요청 중 오류가 발생했습니다. 다시 시도해주세요.');
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

function showSignupGuide() {
    const signupGuide = document.querySelector('.signup-guide');
    if (signupGuide) {
        signupGuide.style.display = 'block';

        // 스크롤을 회원가입 안내 섹션으로 부드럽게 이동
        signupGuide.scrollIntoView({ behavior: 'smooth' });
    }
}

document.querySelector('.request-btn').addEventListener('click', (e) => {
    e.preventDefault();
    showSignupGuide();
});

// document.querySelectorAll('.signup-btn').forEach(btn => {
//     btn.addEventListener('click', (e) => {
//         const signupType = e.currentTarget.classList[1]; // email, kakao, naver, payco

//         switch(signupType) {
//             case 'email':
//                 window.location.href = '/accounts/signup/';
//                 break;
//             case 'kakao':
//                 window.location.href = '/accounts/kakao/login/';
//                 break;
//             case 'naver':
//                 window.location.href = '/accounts/naver/login/';
//                 break;
//             case 'payco':
//                 window.location.href = '/accounts/payco/login/';
//                 break;
//         }
//     });
// });
