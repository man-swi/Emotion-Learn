document.addEventListener('DOMContentLoaded', () => {
    const emotionSelect = document.getElementById('emotionSelect');
    const learnContentDiv = document.getElementById('learnContent');
    // const visualEmotionSelectorArea = document.getElementById('visualEmotionSelectorArea'); // For visual selectors

    // Function to fetch and display learning content
    async function loadLearnContent() {
        const selectedEmotion = emotionSelect.value;
        learnContentDiv.innerHTML = ''; // Clear previous content

        if (!selectedEmotion) {
            learnContentDiv.innerHTML = '<p class="text-center text-muted" style="font-size: 1.1em;">Select an emotion from the dropdown above to begin your exploration.</p>';
            // updateVisualSelectors(null); // Clear active state in visual selectors
            return;
        }

        learnContentDiv.innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div> <p class="mt-2">Loading content...</p></div>';
        // updateVisualSelectors(selectedEmotion); // Highlight active visual selector

        try {
            const response = await fetch(`/api/learn_data/${selectedEmotion}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();

            if (data.error) {
                learnContentDiv.innerHTML = `<div class="alert alert-danger" role="alert">Error: ${data.error}</div>`;
            } else {
                let contentHTML = `<div class="emotion-card-header">`;
                if (data.emoji_url) {
                    contentHTML += `<img src="${data.emoji_url}" alt="${data.name} emoji" class="emotion-card-emoji">`;
                }
                contentHTML += `<h2>${data.name || 'Emotion'}</h2></div>`; // Emotion name as title

                if (data.description) {
                    contentHTML += `<p class="emotion-description">${data.description}</p>`;
                    contentHTML += `<button class="btn btn-primary action-button-learn read-aloud-btn" data-emotion="${data.name}"><i class="fas fa-volume-up"></i>Read Description</button>`;
                } else {
                    contentHTML += `<p>No description available.</p>`;
                }

                if (data.key_features && data.key_features.length > 0) {
                    contentHTML += `<h3 class="mt-4">Key Features:</h3><ul class="key-features-list">`;
                    data.key_features.forEach(feature => {
                        const escapedFeature = feature.replace(/</g, "<").replace(/>/g, ">");
                        contentHTML += `<li><i class="fas fa-check"></i>${escapedFeature}</li>`;
                    });
                    contentHTML += `</ul>`;
                } else {
                    contentHTML += `<p class="mt-3">No specific key features listed.</p>`;
                }

                contentHTML += `<h3 class="mt-4">Reference & Sound:</h3><div class="reference-sound-section">`;
                if (data.emoji_url) { // Show emoji again if preferred in this section
                    // contentHTML += `<span class="emoji-container"><img src="${data.emoji_url}" alt="${data.name} emoji"></span>`;
                }
                if (data.sound_available) {
                   contentHTML += `<button class="btn btn-info action-button-learn sound-cue-btn" data-emotion="${data.name}"><i class="fas fa-play-circle"></i>Play Sound for ${data.name}</button>`;
                } else {
                    contentHTML += `<p class="text-muted ml-2">(No sound cue available)</p>`
                }
                contentHTML += `</div>`;

                if (data.image_urls && data.image_urls.length > 0) {
                    contentHTML += `<h3 class="mt-4">Example Images:</h3>`;
                    contentHTML += `<p class="text-muted"><small>Click on an image to enlarge.</small></p>`;
                    contentHTML += `<div class="example-images-gallery">`;
                    data.image_urls.forEach(url => {
                        // Wrap images in <a> tags for Magnific Popup
                        contentHTML += `<a href="${url}" class="gallery-item mfp-image" title="Example of ${data.name}">
                                           <img src="${url}" alt="Example of ${data.name}">
                                        </a>`;
                    });
                    contentHTML += `</div>`;
                } else {
                     contentHTML += `<h3 class="mt-4">Example Images:</h3><p>No example images available.</p>`;
                }

                learnContentDiv.innerHTML = contentHTML;

                // Initialize Magnific Popup for the gallery
                $('.example-images-gallery').magnificPopup({
                    delegate: 'a.mfp-image', // child items selector, by clicking on it popup will open
                    type: 'image',
                    gallery:{enabled:true},
                    removalDelay: 300,
                    mainClass: 'mfp-fade', // Animation class
                    image: {
                        titleSrc: 'title' // Attribute for the title
                    }
                });


                // Add Event Listeners to dynamically added buttons
                const readAloudButton = learnContentDiv.querySelector('.read-aloud-btn');
                if (readAloudButton) {
                    readAloudButton.addEventListener('click', handleReadAloudClick);
                }
                const soundCueButton = learnContentDiv.querySelector('.sound-cue-btn');
                if (soundCueButton) {
                    soundCueButton.addEventListener('click', handlePlaySoundCueClick);
                }
            }

        } catch (error) {
            console.error('Error fetching or displaying learning data:', error);
            learnContentDiv.innerHTML = `<div class="alert alert-warning" role="alert">Could not load learning data. Please check the console or try again later.</div>`;
        }
    }

    // /* Optional: Function to populate and handle visual emotion selectors */
    // async function populateVisualSelectors() {
    //     if (!visualEmotionSelectorArea) return;
    //     // Fetch all emotions (or use the one from the dropdown)
    //     // This part might need a new API endpoint or to reuse learn_page data
    //     const emotions = Array.from(emotionSelect.options)
    //                           .map(opt => opt.value)
    //                           .filter(val => val !== "");
        
    //     // For simplicity, assume we have emoji URLs available somehow, or fetch them
    //     // This is a placeholder - you'd need to get emoji URLs for each emotion
    //     const emojiMap = { /* 'Happy': '/static/emojis/happy.png', ... */ };

    //     let visualHTML = '';
    //     emotions.forEach(emotion => {
    //         const emojiSrc = emojiMap[emotion] || '/static/emojis/neutral.png'; // Fallback
    //         visualHTML += `<button class="btn-emotion" data-emotion="${emotion}">
    //                             <img src="${emojiSrc}" alt="${emotion}">
    //                             <span>${emotion}</span>
    //                        </button>`;
    //     });
    //     visualEmotionSelectorArea.innerHTML = visualHTML;

    //     document.querySelectorAll('.btn-emotion').forEach(button => {
    //         button.addEventListener('click', (e) => {
    //             const selected = e.currentTarget.dataset.emotion;
    //             emotionSelect.value = selected;
    //             loadLearnContent(); // This will also call updateVisualSelectors
    //         });
    //     });
    // }
    // /* Function to update active state of visual selectors */
    // function updateVisualSelectors(activeEmotion) {
    //     if (!visualEmotionSelectorArea) return;
    //     document.querySelectorAll('.btn-emotion').forEach(button => {
    //         if (button.dataset.emotion === activeEmotion) {
    //             button.classList.add('active');
    //         } else {
    //             button.classList.remove('active');
    //         }
    //     });
    // }


    emotionSelect.addEventListener('change', loadLearnContent);
    // populateVisualSelectors(); // Call if implementing visual selectors
    loadLearnContent(); // Load content for initially selected (if any) or show placeholder

}); // End of DOMContentLoaded

async function handlePlaySoundCueClick(event) {
    const emotionName = event.target.dataset.emotion;
    if (!emotionName) return;
    
    event.target.disabled = true;
    const originalText = event.target.innerHTML;
    event.target.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Playing...`;

    try {
        const response = await fetch(`/api/play_sound/${emotionName}`);
        const result = await response.json();
        if (result.status !== 'success') {
            console.warn(`Could not play sound: ${result.message || 'Unknown reason'}`);
            // Optionally provide user feedback e.g. using a small toast notification
        }
    } catch (error) {
        console.error('Error triggering sound cue API:', error);
    } finally {
        event.target.disabled = false;
        event.target.innerHTML = originalText;
    }
}

async function handleReadAloudClick(event) {
    const emotionName = event.target.dataset.emotion;
    if (!emotionName) return;

    event.target.disabled = true;
    const originalText = event.target.innerHTML;
    event.target.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Speaking...`;

    try {
        const response = await fetch(`/api/speak_description/${emotionName}`);
        const result = await response.json();
        if (result.status !== 'success') {
            console.error('TTS Error:', result.message);
            alert(`Could not read description: ${result.message || 'Unknown TTS error'}`);
        }
    } catch (error) {
        console.error('Error calling speak description API:', error);
        alert('Failed to trigger description playback.');
    } finally {
        event.target.disabled = false;
        event.target.innerHTML = originalText;
    }
}
