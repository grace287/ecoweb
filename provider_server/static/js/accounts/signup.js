function updateFileName(input) {
    const fileName = input.files[0]?.name || '선택된 파일 없음';
    input.parentElement.querySelector('.file-name').textContent = fileName;
}

document.querySelector('.file-upload-btn').addEventListener('click', function() {
    document.querySelector('.file-upload-input').click();
});

// 선택된 분야들을 저장할 배열
let selectedFields = [];

// 모달 표시
function showFieldModal() {
    document.getElementById('fieldModal').style.display = 'block';
    // 이미 선택된 분야들에 대해 체크박스 체크
    selectedFields.forEach(field => {
        const checkbox = document.querySelector(`input[value="${field.value}"]`);
        if (checkbox) checkbox.checked = true;
    });
}

// 모달 닫기
function closeFieldModal() {
    document.getElementById('fieldModal').style.display = 'none';
}

// 선택 확인
function confirmFieldSelection() {
    const checkboxes = document.querySelectorAll('input[name="fields"]:checked');
    selectedFields = Array.from(checkboxes).map(cb => ({
        value: cb.value,
        label: cb.parentElement.textContent.trim()
    }));
    
    // 선택된 분야 표시 업데이트
    updateSelectedFields();
    closeFieldModal();
}

// 선택된 분야 표시 업데이트
function updateSelectedFields() {
    const container = document.querySelector('.selected-fields');
    container.innerHTML = selectedFields.map(field => `
        <div class="field-tag">
            ${field.label}
            <span class="remove-field" onclick="removeField('${field.value}')">&times;</span>
        </div>
    `).join('');
    
    // 선택된 분야를 hidden input에 저장
    const hiddenInput = document.getElementById('selected_fields');
    if (!hiddenInput) {
        const input = document.createElement('input');
        input.type = 'hidden';
        input.id = 'selected_fields';
        input.name = 'selected_fields';
        document.querySelector('form').appendChild(input);
    }
    document.getElementById('selected_fields').value = JSON.stringify(selectedFields);
}

// 분야 제거
function removeField(value) {
    selectedFields = selectedFields.filter(field => field.value !== value);
    updateSelectedFields();
}

// 모달 외부 클릭 시 닫기
window.onclick = function(event) {
    const modal = document.getElementById('fieldModal');
    if (event.target == modal) {
        closeFieldModal();
    }
}

// ESC 키로 모달 닫기
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeFieldModal();
    }
});