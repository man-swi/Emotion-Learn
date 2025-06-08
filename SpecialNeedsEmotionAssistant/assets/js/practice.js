// START OF FILE SpecialNeedsEmotionAssistant/assets/js/practice.js
document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('webcam');
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    const emotionLabel = document.getElementById('emotionLabel');
    const emotionEmoji = document.getElementById('emotionEmoji');
    const startStopButton = document.getElementById('startStopButton');
    const cameraStatus = document.getElementById('cameraStatus');
    const detectionResultDiv = document.getElementById('detectionResult');

    const targetEmotionSelect = document.getElementById('targetEmotionSelect');
    const instructionArea = document.getElementById('instructionArea');
    const instructionText = instructionArea.querySelector('p');

    // Optional Confidence Bar Elements
    // const confidenceBarContainer = document.querySelector('.confidence-bar-container');
    // const confidenceFill = document.getElementById('confidenceFill');
    // const confidenceText = document.getElementById('confidenceText');


    let stream = null;
    let intervalId = null;
    let isDetecting = false;
    const detectionInterval = 300; 

    let lastDisplayedEmotion = 'Neutral';
    let lastPlayedSound = null;
    let currentTargetEmotion = ''; 

    let emojiUrls = {}; 

    function storeEmojiUrl(emotion, url) {
        if (emotion && url) emojiUrls[emotion] = url;
    }

    function updateInstructions() {
        currentTargetEmotion = targetEmotionSelect.value;
        if (currentTargetEmotion) {
            instructionText.innerHTML = `Try to make a "<strong>${currentTargetEmotion}</strong>" face!`;
        } else {
            instructionText.textContent = 'Practice freely! Try making different faces.';
        }
        detectionResultDiv.classList.remove('feedback-correct', 'feedback-incorrect');
    }

    async function startCamera() {
        if (stream) {
             stopCamera();
             await new Promise(resolve => setTimeout(resolve, 150));
        }
        try {
            console.log("Attempting to start camera...");
            cameraStatus.textContent = 'Starting camera...';
            stream = await navigator.mediaDevices.getUserMedia({
                 video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: "user" },
                 audio: false
             });
            video.srcObject = stream;
            video.style.display = 'block';
            cameraStatus.style.display = 'none';

            await video.play();
            console.log("Camera stream active.");

            emotionLabel.textContent = 'Initializing detection...';
            emotionEmoji.src = '#'; 
            emotionEmoji.style.display = 'none';
            // if (confidenceBarContainer) confidenceBarContainer.style.display = 'none'; // Hide confidence bar
            // if (confidenceText) confidenceText.style.display = 'none';

            detectionResultDiv.classList.remove('feedback-correct', 'feedback-incorrect');
            startStopButton.innerHTML = '<i class="fas fa-video-slash"></i> Stop Camera';
            isDetecting = true;
            lastDisplayedEmotion = 'Neutral'; 
            lastPlayedSound = null;
            updateInstructions(); 

            if(intervalId) clearInterval(intervalId);
            intervalId = setInterval(detectEmotion, detectionInterval);

        } catch (err) {
            console.error("Error accessing webcam: ", err);
            cameraStatus.textContent = `Error: ${err.name}. Check permissions.`;
            cameraStatus.style.display = 'block';
            video.style.display = 'none';
            alert(`Could not access webcam: ${err.name} - ${err.message}.\nPlease ensure camera access is allowed in your browser settings and no other app is using it.`);
            isDetecting = false;
            startStopButton.innerHTML = '<i class="fas fa-video"></i> Start Camera';
            if (intervalId) clearInterval(intervalId);
            intervalId = null;
            stream = null;
        }
    }

     function stopCamera() {
        console.log("Stopping camera...");
        if (intervalId) { clearInterval(intervalId); intervalId = null; }

        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            video.srcObject = null;
            stream = null;
        }

        video.style.display = 'none';
        cameraStatus.textContent = 'Camera is off. Click "Start Camera".';
        cameraStatus.style.display = 'block';

        emotionLabel.textContent = 'Detection stopped.';
        emotionEmoji.style.display = 'none';
        // if (confidenceBarContainer) confidenceBarContainer.style.display = 'none';
        // if (confidenceText) confidenceText.style.display = 'none';

        detectionResultDiv.classList.remove('feedback-correct', 'feedback-incorrect');
        startStopButton.innerHTML = '<i class="fas fa-video"></i> Start Camera';
        isDetecting = false;
        lastDisplayedEmotion = 'Neutral';
        lastPlayedSound = null;
        instructionText.textContent = 'Select a target emotion above or practice freely!';
        console.log("Camera and detection stopped.");
    }

     async function detectEmotion() {
        if (!isDetecting || !stream || video.readyState < video.HAVE_CURRENT_DATA || video.paused || video.ended) {
             return;
        }

        try {
            if (canvas.width !== video.videoWidth || canvas.height !== video.videoHeight) {
                 if (video.videoWidth > 0 && video.videoHeight > 0) {
                     canvas.width = video.videoWidth;
                     canvas.height = video.videoHeight;
                 } else {
                     return; 
                 }
            }
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
        } catch (e) {
            console.error("Error drawing video frame to canvas:", e);
            return;
        }

        const imageData = canvas.toDataURL('image/jpeg', 0.7);

        try {
            const response = await fetch('/api/process_frame', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', },
                body: JSON.stringify({ imageData: imageData }),
            });

            if (!response.ok) {
                let errorMsg = `Backend error: ${response.status}`;
                try { const errorData = await response.json(); errorMsg += ` - ${errorData.error || 'Unknown'}`; } catch(e){}
                console.error('Frame processing API error:', errorMsg);
                updateDetectionUI({ emotion: lastDisplayedEmotion, error: "Backend communication failed" });
                return;
            }
            const result = await response.json();
            updateDetectionUI(result);

        } catch (error) {
            console.error('Error sending frame or processing response:', error);
             updateDetectionUI({ emotion: lastDisplayedEmotion, error: "Network error" });
        }
    }

    function updateDetectionUI(result) {
        let detectedEmotion = result.emotion || 'Neutral';
        let soundIsAvailable = result.sound_available === true;
        let currentEmojiUrl = result.emoji_url || emojiUrls[detectedEmotion];
        // let confidenceScore = result.confidence || 0; // Assuming backend might send this

        if (result.emoji_url) {
            storeEmojiUrl(detectedEmotion, result.emoji_url);
        }

        let feedbackText = `Detected: <strong>${detectedEmotion}</strong>`;
        detectionResultDiv.classList.remove('feedback-correct', 'feedback-incorrect');

        if (currentTargetEmotion) {
            if (detectedEmotion === currentTargetEmotion && detectedEmotion !== 'Neutral') { // Only "correct" if not Neutral or matches Neutral target
                feedbackText = `<i class="fas fa-check-circle mr-1" style="color: green;"></i> Correct! Detected: <strong>${detectedEmotion}</strong>`;
                detectionResultDiv.classList.add('feedback-correct');
            } else if (detectedEmotion !== currentTargetEmotion) {
                feedbackText = `<i class="fas fa-times-circle mr-1" style="color: red;"></i> Detected: <strong>${detectedEmotion}</strong> (Aiming for: ${currentTargetEmotion})`;
                detectionResultDiv.classList.add('feedback-incorrect');
            } else { // Is Neutral, or matches Neutral target
                feedbackText = `Detected: <strong>${detectedEmotion}</strong>`;
            }
        }
        emotionLabel.innerHTML = feedbackText;

        if (detectedEmotion && currentEmojiUrl) {
            if (emotionEmoji.style.display === 'none' || emotionEmoji.src !== currentEmojiUrl) {
                 emotionEmoji.src = currentEmojiUrl;
                 emotionEmoji.style.display = 'block';
                 emotionEmoji.classList.add('emoji-pop'); // Add animation class
                 setTimeout(() => emotionEmoji.classList.remove('emoji-pop'), 300); // Remove after animation
            }
        } else {
            emotionEmoji.style.display = 'none';
        }

        // Update Confidence Bar (if backend provides confidence)
        // if (confidenceBarContainer && confidenceFill && confidenceText && result.hasOwnProperty('confidence')) {
        //     confidenceBarContainer.style.display = 'block';
        //     confidenceText.style.display = 'block';
        //     const confidencePercentage = Math.round(result.confidence * 100);
        //     confidenceFill.style.width = `${confidencePercentage}%`;
        //     confidenceText.textContent = `Confidence: ${confidencePercentage}%`;
        //     if (confidencePercentage < 30) confidenceFill.style.backgroundColor = '#dc3545'; // Red
        //     else if (confidencePercentage < 70) confidenceFill.style.backgroundColor = '#ffc107'; // Yellow
        //     else confidenceFill.style.backgroundColor = '#28a745'; // Green
        // } else if (confidenceBarContainer) {
        //      confidenceBarContainer.style.display = 'none';
        //      if (confidenceText) confidenceText.style.display = 'none';
        // }


        if (detectedEmotion && detectedEmotion !== lastPlayedSound && detectedEmotion !== "Neutral") { // Avoid sound for Neutral changes unless it's the target
             if (currentTargetEmotion && detectedEmotion === currentTargetEmotion && soundIsAvailable) { // Play sound on correct match (and not neutral)
                playSound(detectedEmotion);
             } else if (!currentTargetEmotion && soundIsAvailable) { 
                playSound(detectedEmotion);
             }
            lastPlayedSound = detectedEmotion;
        }
        lastDisplayedEmotion = detectedEmotion;
    }

    startStopButton.addEventListener('click', () => {
        if (isDetecting) {
            stopCamera();
        } else {
            startCamera();
        }
    });

    targetEmotionSelect.addEventListener('change', updateInstructions);

    stopCamera(); 
}); 

async function playSound(emotionName) {
    if (!emotionName) return;
    console.log(`Requesting sound play for: ${emotionName}`);
    try {
        const response = await fetch(`/api/play_sound/${emotionName}`);
        const result = await response.json();
        if (result.status !== 'success') {
            console.warn("Sound playback issue reported by backend:", result.message);
        }
    } catch (error) {
        console.error('Error calling playSound API:', error);
    }
}