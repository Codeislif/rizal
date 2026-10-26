
document.addEventListener("DOMContentLoaded", function () {
    const questions = Array.from(
        document.querySelectorAll(".quiz-question")
    );

    if (questions.length === 0) return;

    let current = 0;
    const progressText = document.getElementById("progress-text");
    const progressBar = document.getElementById("progress-bar");
    const form = document.getElementById("quiz-form");

    function showQuestion(index) {
        current = index;

        questions.forEach((question, i) => {
            question.hidden = i !== current;
        });

        progressText.textContent =
            `Question ${current + 1} of ${questions.length}`;

        progressBar.style.width =
            `${((current + 1) / questions.length) * 100}%`;

        const previous = questions[current].querySelector(".prev-btn");
        previous.disabled = current === 0;

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    document.querySelectorAll(".next-btn").forEach(button => {
        button.addEventListener("click", function () {
            const selected = questions[current].querySelector(
                'input[type="radio"]:checked'
            );

            if (!selected) {
                alert("Please select an answer before continuing.");
                return;
            }

            if (current < questions.length - 1) {
                showQuestion(current + 1);
            }
        });
    });

    document.querySelectorAll(".prev-btn").forEach(button => {
        button.addEventListener("click", function () {
            if (current > 0) showQuestion(current - 1);
        });
    });

    form.addEventListener("submit", function (event) {
        const selected = questions[current].querySelector(
            'input[type="radio"]:checked'
        );

        if (!selected) {
            event.preventDefault();
            alert("Please select an answer before submitting.");
        }
    });

    showQuestion(0);
});
