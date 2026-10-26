
"use strict";

/* ==================================
   MOBILE NAVIGATION
================================== */

function toggleMenu() {
    document.getElementById("navigation").classList.toggle("open");
}

/* ==================================
   LESSON VIEWER
================================== */

function openLesson(id) {
    const card = document.getElementById("content-" + id);
    if (!card) return;

    const title = card.closest(".module-card").querySelector("h3").textContent;

    document.getElementById("lessonTitle").textContent = title;
    document.getElementById("lessonText").textContent = card.textContent.trim();

    document.getElementById("lessonViewer").classList.remove("hidden");
    document.getElementById("lessonViewer").scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

function closeLesson() {
    document.getElementById("lessonViewer").classList.add("hidden");
}

/* ==================================
   QUIZ QUESTIONS
   Keep this order and the answer
   indexes consistent with app.py.
================================== */

const questions = [
    {
        question: "When was José Rizal born?",
        options: [
            "June 19, 1861",
            "June 12, 1898",
            "December 30, 1896",
            "July 4, 1862"
        ],
        answer: 0
    },
    {
        question: "Where was Rizal born?",
        options: ["Dapitan", "Calamba, Laguna", "Cebu City", "Vigan"],
        answer: 1
    },
    {
        question: "What was the title of Rizal's first famous novel?",
        options: [
            "El Filibusterismo",
            "Florante at Laura",
            "Noli Me Tangere",
            "Mi Ultimo Adios"
        ],
        answer: 2
    },
    {
        question: "Which novel was the sequel to Noli Me Tangere?",
        options: [
            "El Filibusterismo",
            "La Solidaridad",
            "Fray Botod",
            "Urbana at Felisa"
        ],
        answer: 0
    },
    {
        question: "What was Rizal's medical specialty?",
        options: [
            "Cardiology",
            "Pediatrics",
            "Dermatology",
            "Ophthalmology"
        ],
        answer: 3
    },
    {
        question: "Where was Rizal exiled in 1892?",
        options: ["Madrid", "Dapitan", "Hong Kong", "Singapore"],
        answer: 1
    },
    {
        question: "Who was Rizal's mother?",
        options: [
            "Teodora Alonso",
            "Narcisa Rizal",
            "Josephine Bracken",
            "Gregoria de Jesus"
        ],
        answer: 0
    },
    {
        question: "In which year was Noli Me Tangere published?",
        options: ["1872", "1891", "1887", "1896"],
        answer: 2
    },
    {
        question: "When was Rizal executed?",
        options: [
            "June 19, 1861",
            "August 30, 1896",
            "June 12, 1898",
            "December 30, 1896"
        ],
        answer: 3
    },
    {
        question: "What was an important purpose of Rizal's writings?",
        options: [
            "To promote awareness and social reform",
            "To become a colonial governor",
            "To establish a trading empire",
            "To replace all schools with armies"
        ],
        answer: 0
    }
];

const quizContainer = document.getElementById("quizQuestions");
const quizForm = document.getElementById("quizForm");
const quizNotice = document.getElementById("quizNotice");

function buildQuiz() {
    quizContainer.innerHTML = questions.map((item, index) => `
        <article class="quiz-question">
            <h3>${index + 1}. ${item.question}</h3>
            ${item.options.map((option, optionIndex) => `
                <label class="quiz-option">
                    <input
                        type="radio"
                        name="answers"
                        value="${optionIndex}"
                        ${optionIndex === 0 ? "required" : ""}
                    >
                    <span>${option}</span>
                </label>
            `).join("")}
        </article>
    `).join("");
}

if (quizContainer && quizForm) {
    buildQuiz();

    quizForm.addEventListener("submit", event => {
        const answered = questions.every((_, index) => {
            return quizForm.querySelector(
                `input[name="answers"]:checked` +
                `:nth-of-type(${index + 1})`
            );
        });

        // Validate each question independently.
        const complete = questions.every((_, index) => {
            return quizForm.querySelector(
                `.quiz-question:nth-child(${index + 1}) input:checked`
            );
        });

        if (!complete) {
            event.preventDefault();
            quizNotice.textContent = "Please answer all 10 questions before submitting.";
            quizNotice.style.color = "#a33d36";
            return;
        }

        quizNotice.textContent = "Submitting your results...";
    });
}

/* ==================================
   MINI GAME HELPERS
================================== */

function shuffle(items) {
    const result = [...items];

    for (let i = result.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [result[i], result[j]] = [result[j], result[i]];
    }

    return result;
}

function getGameArea() {
    return document.getElementById("gameArea");
}

function showGameMessage(message, color = "green") {
    const feedback = document.getElementById("gameFeedback");

    if (feedback) {
        feedback.textContent = message;
        feedback.style.color = color;
    }
}

/* ==================================
   GAME 1: RIZAL TRIVIA
================================== */

let triviaQuestions = [];
let triviaIndex = 0;
let triviaScore = 0;
let triviaLocked = false;

function startTrivia() {
    stopClockGame();

    triviaQuestions = shuffle(questions);
    triviaIndex = 0;
    triviaScore = 0;

    renderTriviaQuestion();
}

function renderTriviaQuestion() {
    const area = getGameArea();

    if (triviaIndex >= triviaQuestions.length) {
        area.innerHTML = `
            <div class="game-icon">🎉</div>
            <h2>Trivia Completed!</h2>
            <h3>${triviaScore} / ${triviaQuestions.length} correct</h3>
            <p>Keep exploring the lessons to improve your score.</p>
            <button class="btn primary" onclick="startTrivia()">Play Again</button>
        `;
        return;
    }

    triviaLocked = false;
    const item = triviaQuestions[triviaIndex];

    area.innerHTML = `
        <h2>🧠 Rizal Trivia</h2>
        <div class="game-stats">
            <span>Question ${triviaIndex + 1} / ${triviaQuestions.length}</span>
            <span>Score: ${triviaScore}</span>
        </div>
        <p class="game-question">${item.question}</p>
        <div class="game-options">
            ${item.options.map((option, index) => `
                <button class="game-option" onclick="answerTrivia(${index})">
                    ${option}
                </button>
            `).join("")}
        </div>
        <p id="gameFeedback" class="feedback" aria-live="polite"></p>
        <button id="triviaNext" class="btn primary" hidden
                onclick="nextTrivia()">Next →</button>
    `;
}

function answerTrivia(selected) {
    if (triviaLocked) return;

    triviaLocked = true;

    const item = triviaQuestions[triviaIndex];

    document.querySelectorAll("#gameArea .game-option")
        .forEach(button => button.disabled = true);

    if (selected === item.answer) {
        triviaScore++;
        showGameMessage("Correct! Great job.", "green");
    } else {
        showGameMessage("Correct answer: " + item.options[item.answer], "#a33d36");
    }

    document.getElementById("triviaNext").hidden = false;
}

function nextTrivia() {
    if (!triviaLocked) return;
    triviaIndex++;
    renderTriviaQuestion();
}

/* ==================================
   GAME 2: MEMORY MATCH
================================== */

let memoryCards = [];
let memoryFirst = null;
let memoryLocked = false;
let memoryMoves = 0;
let memoryMatches = 0;
let memoryTimeout = null;

const memoryPairs = [
    ["1861", "Birth year"],
    ["Calamba", "Birthplace"],
    ["Noli Me Tangere", "First novel"],
    ["El Filibusterismo", "Sequel novel"],
    ["Dapitan", "Place of exile"],
    ["Teodora Alonso", "Mother"],
    ["Ophthalmology", "Medical specialty"],
    ["1896", "Year of execution"]
];

function startMemory() {
    stopClockGame();

    if (memoryTimeout !== null) {
        clearTimeout(memoryTimeout);
        memoryTimeout = null;
    }

    memoryCards = shuffle(
        memoryPairs.flatMap((pair, pairId) => [
            {
                pairId,
                text: pair[0],
                revealed: false,
                matched: false
            },
            {
                pairId,
                text: pair[1],
                revealed: false,
                matched: false
            }
        ])
    );

    memoryFirst = null;
    memoryLocked = false;
    memoryMoves = 0;
    memoryMatches = 0;

    renderMemory();
}

function renderMemory() {
    const area = getGameArea();

    area.innerHTML = `
        <h2>🃏 Memory Match</h2>
        <p>Find matching facts. Try to finish with fewer moves!</p>
        <div class="game-stats">
            <span>Moves: ${memoryMoves}</span>
            <span>Pairs: ${memoryMatches}/${memoryPairs.length}</span>
        </div>
        <div class="memory-grid">
            ${memoryCards.map((card, index) => `
                <button
                    class="memory-card ${card.matched ? "matched" : ""}"
                    onclick="flipMemory(${index})"
                    ${card.matched ? "disabled" : ""}
                >
                    ${card.matched || card.revealed ? card.text : "❔"}
                </button>
            `).join("")}
        </div>
        <p id="gameFeedback" class="feedback" aria-live="polite"></p>
        <button class="btn primary" onclick="startMemory()">Restart Game</button>
    `;
}

function flipMemory(index) {
    if (memoryLocked) return;

    const card = memoryCards[index];

    if (card.matched || card.revealed) return;

    card.revealed = true;

    if (memoryFirst === null) {
        memoryFirst = index;
        renderMemory();
        return;
    }

    const firstIndex = memoryFirst;
    const firstCard = memoryCards[firstIndex];

    memoryMoves++;

    if (firstCard.pairId === card.pairId) {
        firstCard.matched = true;
        card.matched = true;

        memoryMatches++;
        memoryFirst = null;

        renderMemory();

        if (memoryMatches === memoryPairs.length) {
            getGameArea().insertAdjacentHTML(
                "beforeend",
                "<h3>🏆 You matched every pair!</h3><p>Excellent memory!</p>"
            );
        }

        return;
    }

    memoryLocked = true;
    renderMemory();
    showGameMessage("Not a match. Try again!", "#a33d36");

    memoryTimeout = setTimeout(() => {
        memoryCards[firstIndex].revealed = false;
        memoryCards[index].revealed = false;
        memoryFirst = null;
        memoryLocked = false;
        memoryTimeout = null;
        renderMemory();
    }, 850);
}

/* ==================================
   GAME 3: BEAT THE CLOCK
================================== */

let clockInterval = null;
let clockTimeout = null;
let clockQuestions = [];
let clockIndex = 0;
let clockScore = 0;
let clockTime = 30;
let clockLocked = false;

function stopClockGame() {
    if (clockInterval !== null) {
        clearInterval(clockInterval);
        clockInterval = null;
    }

    if (clockTimeout !== null) {
        clearTimeout(clockTimeout);
        clockTimeout = null;
    }
}

function startClockGame() {
    stopClockGame();

    clockQuestions = shuffle(questions);
    clockIndex = 0;
    clockScore = 0;
    clockTime = 30;
    clockLocked = false;

    renderClockQuestion();

    clockInterval = setInterval(() => {
        clockTime--;

        const timer = document.getElementById("clockTimer");

        if (timer) timer.textContent = clockTime;

        if (clockTime <= 0) {
            finishClockGame();
        }
    }, 1000);
}

function renderClockQuestion() {
    if (clockTime <= 0) return;

    if (clockIndex >= clockQuestions.length) {
        clockQuestions = shuffle(questions);
        clockIndex = 0;
    }

    clockLocked = false;

    const item = clockQuestions[clockIndex];

    getGameArea().innerHTML = `
        <h2>⏱️ Beat the Clock</h2>
        <div class="game-stats">
            <span>Time: <strong id="clockTimer">${clockTime}</strong>s</span>
            <span>Score: ${clockScore}</span>
        </div>
        <p class="game-question">${item.question}</p>
        <div class="game-options">
            ${item.options.map((option, index) => `
                <button class="game-option" onclick="answerClock(${index})">
                    ${option}
                </button>
            `).join("")}
        </div>
        <p id="gameFeedback" class="feedback" aria-live="polite"></p>
    `;
}

function answerClock(selected) {
    if (clockLocked || clockTime <= 0) return;

    clockLocked = true;

    const item = clockQuestions[clockIndex];

    document.querySelectorAll("#gameArea .game-option")
        .forEach(button => button.disabled = true);

    if (selected === item.answer) {
        clockScore++;
        showGameMessage("Correct! +1 point", "green");
    } else {
        showGameMessage("Correct answer: " + item.options[item.answer], "#a33d36");
    }

    clockIndex++;

    clockTimeout = setTimeout(() => {
        clockTimeout = null;

        if (clockTime > 0 && clockInterval !== null) {
            renderClockQuestion();
        }
    }, 450);
}

function finishClockGame() {
    stopClockGame();

    getGameArea().innerHTML = `
        <div class="game-icon">⏰</div>
        <h2>Time's Up!</h2>
        <h1>${clockScore} points</h1>
        <p>Can you beat your score next time?</p>
        <button class="btn primary" onclick="startClockGame()">Play Again</button>
    `;
}
