
document.addEventListener('DOMContentLoaded', () => {
    const nextQuestionButton = document.getElementById('nextQuestionButton');
    const questionContentDiv = document.getElementById('questionContent');
    const feedbackArea = document.getElementById('feedbackArea');
    const scoreArea = document.getElementById('scoreArea');

    let currentCorrectAnswer = null;
    let questionsAnswered = 0;
    let correctAnswers = 0;
    let quizStarted = false;

    updateScoreDisplay(); 

    async function loadNextQuestion() {
        feedbackArea.innerHTML = '';
        feedbackArea.className = ''; // Clear style classes
        questionContentDiv.innerHTML = '<div class="text-center p-4"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div> <p class="mt-2">Loading question...</p></div>';
        nextQuestionButton.disabled = true; // Disable while loading/processing
        
        let questionLoadedSuccessfully = false; // Flag to track success of current load

        if (!quizStarted) {
            quizStarted = true;
            questionsAnswered = 0; 
            correctAnswers = 0;
            updateScoreDisplay();
            // Button text will change to "Next Question" upon successful first load
        }

        try {
            const response = await fetch('/api/quiz_question');
            if (!response.ok) {
                let errorDetail = `HTTP error! status: ${response.status}`;
                try {
                    const errorJson = await response.json();
                    errorDetail = errorJson.error || errorDetail;
                } catch (e) { /* ignore if response is not json */ }
                throw new Error(errorDetail);
            }
            const data = await response.json();

            if (data.error) {
                questionContentDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error loading question: ${data.error}</div>`;
                currentCorrectAnswer = null; // Ensure no stale correct answer
                questionLoadedSuccessfully = false;
            } else {
                currentCorrectAnswer = data.correct_answer;
                displayQuestion(data); // This will also ensure nextQuestionButton is disabled
                nextQuestionButton.innerHTML = '<i class="fas fa-arrow-right"></i> Next Question';
                questionLoadedSuccessfully = true;
            }

        } catch (error) {
            console.error('Error fetching quiz question:', error);
            questionContentDiv.innerHTML = `<div class="alert alert-warning" role="alert">Could not load quiz question: ${error.message}. Please try again.</div>`;
            currentCorrectAnswer = null; // Ensure no stale correct answer
            questionLoadedSuccessfully = false;
        } finally {
            if (!questionLoadedSuccessfully) {
                // If question loading failed at any point (network, HTTP, or data.error)
                nextQuestionButton.innerHTML = '<i class="fas fa-redo"></i> Try Again';
                nextQuestionButton.disabled = false; // Enable for retry
            }
        }
    }

    function displayQuestion(data) {
        let questionHTML = `<h3>What emotion is shown?</h3>`;
        if (data.image_url) {
            questionHTML += `<img src="${data.image_url}" alt="Emotion to identify" id="questionImage">`;
        } else {
             questionHTML += `<p class="text-danger">(Image could not be loaded for this question)</p>`;
        }

        questionHTML += `<div class="quiz-options">`;
        if (data.options && data.options.length > 0) {
            data.options.forEach(option => {
                const escapedOption = option.replace(/</g, "<").replace(/>/g, ">");
                questionHTML += `<button class="answer-button" data-answer="${escapedOption}">${escapedOption}</button>`;
            });
        } else {
             questionHTML += `<p class="text-warning">(No options provided for this question)</p>`;
        }
        questionHTML += `</div>`;

        questionContentDiv.innerHTML = questionHTML;

        document.querySelectorAll('.answer-button').forEach(button => {
            button.addEventListener('click', handleAnswerClick);
        });
        nextQuestionButton.disabled = true; 
    }

    async function handleAnswerClick(event) {
        const chosenAnswer = event.target.dataset.answer;
        if (!currentCorrectAnswer) {
            console.error("Cannot check answer, correct answer not set.");
            return; 
        }

        document.querySelectorAll('.answer-button').forEach(button => {
            button.disabled = true; 
            if (button.dataset.answer === currentCorrectAnswer) {
                button.classList.add('highlight-correct'); 
            }
        });
        if (chosenAnswer !== currentCorrectAnswer) {
             event.target.classList.add('highlight-incorrect');
        }
       
        questionsAnswered++;

        try {
            const response = await fetch('/api/check_answer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({
                    chosen_answer: chosenAnswer,
                    correct_answer: currentCorrectAnswer
                }),
            });
            if (!response.ok) {
                let errorDetail = `HTTP error checking answer! status: ${response.status}`;
                try {
                    const errorJson = await response.json();
                    errorDetail = errorJson.error || errorDetail;
                } catch (e) {}
                throw new Error(errorDetail);
            }
            
            const result = await response.json();

            let feedbackHTML = '';
            let feedbackIcon = '';

            if (result.is_correct) {
                correctAnswers++;
                feedbackIcon = '<i class="fas fa-check-circle mr-2" style="color: green;"></i>';
                feedbackHTML = `<span>Correct!</span>`;
                feedbackArea.className = 'correct-feedback';
                
            } else {
                feedbackIcon = '<i class="fas fa-times-circle mr-2" style="color: red;"></i>';
                const escapedCorrect = result.correct_answer.replace(/</g, "<").replace(/>/g, ">");
                feedbackHTML = `<span>Incorrect. The correct answer was: <strong>${escapedCorrect}</strong></span>`;
                feedbackArea.className = 'incorrect-feedback';
            }

            if (result.correct_emoji_url) {
                feedbackHTML += `<img src="${result.correct_emoji_url}" alt="${result.correct_answer}" class="feedback-emoji">`;
            }
            feedbackArea.innerHTML = feedbackIcon + feedbackHTML;

            if (result.is_correct && result.sound_available) {
                playSound(result.correct_answer);
            }

        } catch (error) {
            console.error('Error checking answer:', error);
            feedbackArea.innerHTML = `<p class="text-danger">Could not check answer: ${error.message}.</p>`;
            feedbackArea.className = ''; 
        } finally {
             updateScoreDisplay();
             nextQuestionButton.disabled = false; 
        }
    }

    function updateScoreDisplay() {
        scoreArea.textContent = `Score: ${correctAnswers} / ${questionsAnswered}`;
    }

    nextQuestionButton.addEventListener('click', loadNextQuestion);

    questionContentDiv.innerHTML = '<p class="lead mt-3">Click the "Start Quiz" button to test your knowledge!</p>';
    nextQuestionButton.disabled = false; 

}); 

async function playSound(emotionName) {
     if (!emotionName) {
        console.warn("playSound called with no emotion name.");
        return;
     }
    // console.log(`Requesting sound for quiz feedback: ${emotionName}`); // Can be a bit noisy
     try {
         const response = await fetch(`/api/play_sound/${emotionName}`);
         const result = await response.json();
         if (result.status !== 'success') {
             console.warn("Sound playback issue during quiz feedback:", result.message);
         }
     } catch (error) {
         console.error('Error triggering sound API during quiz feedback:', error);
     }
}
