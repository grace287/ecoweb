document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('.signup-form');
    const steps = document.querySelectorAll('.progress-step');
    const sections = document.querySelectorAll('.form-section');
    let currentStep = 1;

    // 주소 검색 함수
    window.searchAddress = function() {
        new daum.Postcode({
            oncomplete: function(data) {
                document.getElementById('address').value = data.roadAddress;
                document.getElementById('address_detail').focus();
            }
        }).open();
    };

    // 이메일 중복 확인
    async function checkEmailDuplicate(email) {
        try {
            const response = await fetch('/accounts/check-email/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({ email })
            });
            const data = await response.json();
            return data.available;
        } catch (error) {
            console.error('이메일 중복 확인 오류:', error);
            return false;
        }
    }

    // 비밀번호 유효성 검사
    function validatePassword(password) {
        const minLength = 8;
        const hasNumber = /\d/.test(password);
        const hasLetter = /[a-zA-Z]/.test(password);
        const hasSpecial = /[!@#$%^&*]/.test(password);

        return password.length >= minLength && hasNumber && hasLetter && hasSpecial;
    }

    // 단계 변경 함수
    function updateStep(step) {
        steps.forEach((s, index) => {
            if (index + 1 <= step) {
                s.classList.add('active');
                s.classList.add('slide-in');
            } else {
                s.classList.remove('active');
            }
        });

        sections.forEach((section, index) => {
            if (index + 1 === step) {
                section.style.display = 'block';
                section.classList.add('fade-in');
            } else {
                section.style.display = 'none';
            }
        });

        currentStep = step;
    }

    // 이메일 중복 확인 버튼 이벤트
    document.querySelector('.verify-btn').addEventListener('click', async function() {
        const emailInput = document.getElementById('email');
        const email = emailInput.value;

        if (!email) {
            alert('이메일을 입력해주세요.');
            return;
        }

        const isAvailable = await checkEmailDuplicate(email);
        if (isAvailable) {
            alert('사용 가능한 이메일입니다.');
            emailInput.dataset.verified = 'true';
        } else {
            alert('이미 사용중인 이메일입니다.');
            emailInput.dataset.verified = 'false';
        }
    });

    // 폼 제출 처리
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        if (currentStep === 1) {
            // 첫 번째 단계 유효성 검사
            const email = document.getElementById('email');
            const password = document.getElementById('password');
            const passwordConfirm = document.getElementById('password_confirm');

            if (email.dataset.verified !== 'true') {
                alert('이메일 중복 확인이 필요합니다.');
                return;
            }

            if (!validatePassword(password.value)) {
                alert('비밀번호는 8자 이상, 숫자, 문자, 특수문자를 포함해야 합니다.');
                return;
            }

            if (password.value !== passwordConfirm.value) {
                alert('비밀번호가 일치하지 않습니다.');
                return;
            }

            updateStep(2);
        } else if (currentStep === 2) {
            // 두 번째 단계 유효성 검사
            const company = document.getElementById('company');
            const phone = document.getElementById('phone');
            const address = document.getElementById('address');

            if (!company.value || !phone.value || !address.value) {
                alert('모든 필수 정보를 입력해주세요.');
                return;
            }

            // 최종 제출
            const formData = new FormData(this);
            try {
                const response = await fetch('/accounts/signup/', {
                    method: 'POST',
                    body: formData
                });

                if (response.ok) {
                    updateStep(3);
                    window.location.href = '/accounts/signup-success/';
                } else {
                    alert('회원가입 처리 중 오류가 발생했습니다.');
                }
            } catch (error) {
                console.error('회원가입 오류:', error);
                alert('회원가입 처리 중 오류가 발생했습니다.');
            }
        }
    });
});