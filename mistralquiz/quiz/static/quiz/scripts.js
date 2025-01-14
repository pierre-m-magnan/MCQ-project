document.getElementById('link-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const link = document.getElementById('link').value;
    document.getElementById('loader').style.display = 'block';
    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('score-container').style.display = 'none';
    const response = await fetch('/submit-link/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ link })
    });
    const quiz = await response.json();
    document.getElementById('loader').style.display = 'none';

    displayQuiz(quiz);
});

function displayQuiz(quiz) {
    const quizForm = document.getElementById('quiz-form');
    quizForm.innerHTML = '';
    console.log(quiz.questions)
    quiz.questions.forEach((question, index) => {
        const questionDiv = document.createElement('div');
        questionDiv.className = 'question';
        questionDiv.innerHTML = `<p>${question.question}</p>`;
        question.choices.forEach(option => {
            const optionInput = document.createElement('input');
            optionInput.type = 'radio';
            optionInput.name = `question-${index}`;
            optionInput.value = option;
            const optionLabel = document.createElement('label');
            optionLabel.innerHTML = option;
            questionDiv.appendChild(optionInput);
            questionDiv.appendChild(optionLabel);
            questionDiv.appendChild(document.createElement('br'));
        });
        quizForm.appendChild(questionDiv);
    });
    document.getElementById('quiz-container').style.display = 'block';
}

document.getElementById('submit-quiz-btn').addEventListener('click', async () => {
    const quizForm = document.getElementById('quiz-form');
    const answers = [];
    Array.from(quizForm.elements).forEach(element => {
        if (element.type === 'radio' && element.checked) {
            const questionId = element.name.split('-')[1];
            const selectedOptionIndex = element.value;
            answers.push({ questionId, selectedOptionIndex });
        }
    });
    console.log(answers)
    const response = await fetch('/submit-quiz/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers })
    });
    const result = await response.json();
    document.getElementById('score').innerText = `Votre score est : ${result.score}`;
    document.getElementById('score-container').style.display = 'block';

    result.results.forEach(result => {
        const questionId = result.questionId;
        const isCorrect = result.isCorrect;
        const questionDiv = document.querySelector(`input[name="question-${questionId}"]:checked`).parentElement;
        if (isCorrect) {
            questionDiv.classList.add('correct');
        } else {
            questionDiv.classList.add('incorrect');
        }
    });
});