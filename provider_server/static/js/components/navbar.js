document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggle = document.querySelector('.dropdown-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    dropdownToggle.addEventListener('click', function(event) {
        event.preventDefault(); // 기본 링크 동작 방지
        dropdownMenu.classList.toggle('show'); // 드롭다운 토글
    });
});