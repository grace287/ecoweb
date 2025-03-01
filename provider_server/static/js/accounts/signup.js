document.addEventListener("DOMContentLoaded", function () {
    setupFormValidation();
    setupCategorySelection();
    setupFileUpload();
    setupAddressSearch();
});


// ✅ Django에서 전달한 서비스 카테고리 데이터를 JavaScript 변수로 저장
const categoriesData = JSON.parse('{{ categories|safe }}');
    
document.addEventListener("DOMContentLoaded", function () {
    setupCategorySelection();
});

// ✅ 서비스 카테고리 목록 표시
function displayCategories(categories) {
    const fieldCategoriesList = document.getElementById("fieldCategoriesList");
    if (!fieldCategoriesList) return;

    fieldCategoriesList.innerHTML = categories.map(category => `
        <div class="category-option">
            <label>
                <input type="checkbox" value="${category.id}" data-name="${category.name}" onchange="toggleCategorySelection(this)">
                ${category.name} (${category.id})
            </label>
        </div>
    `).join("");
}

function searchCategories() {
    const searchTerm = document.getElementById("categorySearch").value.toLowerCase();
    const filteredCategories = categoriesData.filter(category =>
        category.name.toLowerCase().includes(searchTerm) ||
        String(category.id).includes(searchTerm)
    );
    displayCategories(filteredCategories);
}

function toggleModal(modalId, show = true) {
    document.getElementById(modalId).style.display = show ? "block" : "none";
    if (show) displayCategories(categoriesData);  // ✅ 모달이 열릴 때 카테고리 목록 업데이트
}

// ✅ 폼 제출 전 유효성 검사 및 API 요청
function setupFormValidation() {
    const signupForm = document.getElementById("signupForm");

    if (!signupForm) {
        console.error("⚠️ signupForm 요소를 찾을 수 없습니다.");
        return;
    }

    signupForm.addEventListener("submit", function (e) {
        e.preventDefault(); // 기본 제출 방지

        const requiredFields = [
            "username", "email", "password", "password-confirm",
            "company_name", "business_registration_number",
            "business_phone_number", "address"
        ];

        for (const fieldId of requiredFields) {
            const field = document.getElementById(fieldId);
            if (!field || !field.value.trim()) {
                showAlert(`${fieldId.replace("_", " ")}을(를) 입력해주세요.`);
                return;
            }
        }

        if (document.getElementById("password").value !== document.getElementById("password-confirm").value) {
            showAlert("비밀번호가 일치하지 않습니다.");
            return;
        }

        const formData = new FormData(signupForm);
        const jsonData = Object.fromEntries(formData.entries());

        fetch("/signup/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(jsonData),
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = data.redirect_url; // 회원가입 성공 후 리디렉션
            } else {
                showAlert(data.error);
            }
        })
        .catch(error => {
            console.error("회원가입 요청 오류:", error);
            showAlert("서버 오류가 발생했습니다. 다시 시도해주세요.");
        });
    });
}

// ✅ CSRF 토큰 가져오기 함수
// function getCSRFToken() {
//     return document.cookie.split("; ")
//         .find(row => row.startsWith("csrftoken="))
//         ?.split("=")[1] || "";
// }

// ✅ 알림 메시지 표시 함수
function showAlert(message, type = "error") {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px;
        border-radius: 4px;
        z-index: 1000;
        background-color: ${type === "error" ? "#f8d7da" : "#d4edda"};
        color: ${type === "error" ? "#721c24" : "#155724"};
        border: 1px solid ${type === "error" ? "#f5c6cb" : "#c3e6cb"};
    `;
    alertDiv.textContent = message;
    document.body.appendChild(alertDiv);

    setTimeout(() => alertDiv.remove(), 3000);
}

// ✅ 파일 업로드 시 파일명 업데이트
function setupFileUpload() {
    document.getElementById("attachment")?.addEventListener("change", function () {
        const fileNames = Array.from(this.files).map(file => file.name).join(", ") || "파일을 선택하세요";
        document.querySelector(".file-name").textContent = fileNames;
    });
}

// ✅ 사업자등록번호 검증 API 호출
function verifyBusinessNumber() {
    const businessNumber = document.getElementById("business_registration_number").value.trim();
    if (!businessNumber) return showAlert("사업자등록번호를 입력해주세요.");

    fetch("{% url 'verify_business_number' %}", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ business_number: businessNumber }),
    })
    .then(response => response.json())
    .then(data => {
        showAlert(data.is_valid ? "유효한 사업자등록번호입니다." : "유효하지 않은 사업자등록번호입니다.");
    })
    .catch(() => showAlert("사업자등록번호 검증 중 오류가 발생했습니다."));
}

// ✅ 주소 검색 기능 (다음 우편번호 API)
function setupAddressSearch() {
    document.getElementById("address")?.addEventListener("click", function () {
        new daum.Postcode({
            oncomplete: function (data) {
                document.getElementById("address").value = data.roadAddress;
                document.getElementById("address_detail").focus();
            },
        }).open();
    });
}

// ✅ 분야 선택 모달 열기 & 닫기
function setupCategorySelection() {
    document.getElementById("categorySearch")?.addEventListener("input", searchCategories);
    document.getElementById("selected_categories_display").innerHTML = ""; // 초기화

    document.querySelector(".search-btn")?.addEventListener("click", function () {
        toggleModal("fieldModal", true);
    });

    document.querySelector(".close-btn")?.addEventListener("click", function () {
        toggleModal("fieldModal", false);
    });
}

// ✅ 카테고리 검색
function searchCategories() {
    const searchTerm = document.getElementById("categorySearch").value.toLowerCase();
    const categories = categoriesData.filter(category =>
        category.name.toLowerCase().includes(searchTerm) ||
        category.category_code.toLowerCase().includes(searchTerm)
    );
    displayCategories(categories);
}

// ✅ 모달 표시
function toggleModal(modalId, show = true) {
    document.getElementById(modalId).style.display = show ? "block" : "none";
}

// ✅ 선택한 카테고리 추가
let selectedCategories = [];
function toggleCategorySelection(checkbox) {
    const categoryCode = checkbox.value;
    const categoryName = checkbox.getAttribute("data-name");

    if (checkbox.checked) {
        if (!selectedCategories.some(cat => cat.code === categoryCode)) {
            selectedCategories.push({ code: categoryCode, name: categoryName });
        }
    } else {
        selectedCategories = selectedCategories.filter(cat => cat.code !== categoryCode);
    }
    updateSelectedCategoriesDisplay();
}

// ✅ 선택된 카테고리 UI 업데이트
function updateSelectedCategoriesDisplay() {
    const selectedCategoriesDisplay = document.getElementById("selected_categories_display");
    const serviceCategoryCodesInput = document.getElementById("service_category_codes");

    selectedCategoriesDisplay.innerHTML = selectedCategories.map(category => `
        <div class="category-tag">
            ${category.name} <span onclick="removeCategory('${category.code}')">×</span>
        </div>
    `).join("");
    serviceCategoryCodesInput.value = JSON.stringify(selectedCategories.map(cat => cat.code));
}

// ✅ 선택한 카테고리 제거
function removeCategory(code) {
    selectedCategories = selectedCategories.filter(cat => cat.code !== code);
    updateSelectedCategoriesDisplay();
}

// ✅ 카테고리 선택 확정
function confirmFieldSelection() {
    toggleModal("fieldModal", false);
    updateSelectedCategoriesDisplay();
}
