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
document.getElementById('login-modal').addEventListener('click', function (event) {
    if (!event.target.closest('.modal-content')) {
        closeModal();
    }
});

// 로그인 폼 제출 이벤트
document.querySelector('.login-form').addEventListener('submit', function(event) {
    event.preventDefault(); // 기본 제출 동작 방지

    const formData = new FormData(this); // 폼 데이터 가져오기

    // AJAX 요청
    fetch('/accounts/login/', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': getCookie('csrftoken') // CSRF 토큰 추가
        }
    })
    .then(response => {
        if (response.ok) {
            // 로그인 성공 시 페이지 리로드
            window.location.reload();
        } else {
            // 로그인 실패 시 에러 메시지 표시
            alert('로그인에 실패했습니다. 아이디와 비밀번호를 확인하세요.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

// CSRF 토큰 가져오기 함수
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