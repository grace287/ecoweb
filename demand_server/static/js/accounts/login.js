// 모달 열기
function openModal() {
    document.getElementById('login-modal').style.display = 'block';
}

// 모달 닫기
function closeModal() {
    document.getElementById('login-modal').style.display = 'none';
}

// 닫기 버튼 이벤트
document.querySelector('.close-btn').addEventListener('click', closeModal);

// 모달 외부 클릭 시 닫기
window.addEventListener('click', function(event) {
    const modal = document.getElementById('login-modal');
    if (event.target === modal) {  // modal-content가 아닌 modal 자체를 클릭했을 때만 닫기
        closeModal();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(this);
        const submitButton = this.querySelector('button[type="submit"]');
        
        try {
            submitButton.disabled = true;
            submitButton.textContent = '로그인 중...';
            
            const response = await fetch('/accounts/login/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                }
            });

            const data = await response.json();
            
            if (data.success) {
                // 로그인 성공 시 메인 페이지로 리다이렉트
                window.location.href = data.redirect_url;
            } else {
                // 에러 메시지 표시
                const errorDiv = document.querySelector('.error-message');
                if (errorDiv) {
                    errorDiv.textContent = data.message;
                    errorDiv.style.display = 'block';
                }
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('로그인 처리 중 오류가 발생했습니다.');
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = '로그인';
        }
    });

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