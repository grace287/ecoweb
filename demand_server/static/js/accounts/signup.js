
    document.addEventListener("DOMContentLoaded", function () {
        const signupForm = document.querySelector(".signup-form");

        signupForm.addEventListener("submit", async function (e) {
            e.preventDefault();

            const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;

            const formData = new FormData(signupForm);
    
            try {
                const response = await fetch("/signup/", {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrftoken,  // ✅ CSRF 토큰 추가
                    },
                    body: formData,  // ✅ JSON이 아닌 FormData 전송
                });

                const data = await response.json();

                if (data.success) {
                    window.location.href = "{% url 'signup_success' %}"; // 가입 성공 시 이동
                } else {
                    alert(data.error); // 에러 메시지 표시
                }
            } catch (error) {
                console.error("Signup error:", error);
                alert("회원가입 처리 중 오류가 발생했습니다.");
            }
        });

        let currentStep = 1;

        function showStep(step) {
            document.querySelectorAll(".form-section").forEach((section, index) => {
                section.style.display = index + 1 === step ? "block" : "none";
            });

            document.querySelectorAll(".progress-step").forEach((stepElement, index) => {
                stepElement.classList.toggle("active", index + 1 <= step);
            });

            currentStep = step;
        }

        window.nextStep = function () {
            if (currentStep < 2) showStep(currentStep + 1);
        };

        window.prevStep = function () {
            if (currentStep > 1) showStep(currentStep - 1);
        };

        // 주소찾기

        window.searchAddress = function () {
            new daum.Postcode({
                oncomplete: function (data) {
                    document.getElementById("address").value = data.roadAddress;
                    document.getElementById("address_detail").focus();
                },
            }).open();
        };

        // 중복 확인 (아이디, 이메일)
    window.checkDuplicate = async function (type) {
        const value = document.getElementById(type).value;
        if (!value) {
            alert(`${type === "username" ? "아이디" : "이메일"}를 입력해주세요.`);
            return;
        }

        try {
            const response = await fetch(`/check-${type}-duplicate/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
                },
                body: JSON.stringify({ [type]: value }),
            });

            const data = await response.json();
            alert(data.is_duplicate ? `이미 사용 중인 ${type === "username" ? "아이디" : "이메일"}입니다.` : `사용 가능한 ${type === "username" ? "아이디" : "이메일"}입니다.`);
        } catch (error) {
            console.error(`${type} 중복 확인 오류:`, error);
            alert(`${type === "username" ? "아이디" : "이메일"} 확인 중 오류가 발생했습니다.`);
        }
    };
});