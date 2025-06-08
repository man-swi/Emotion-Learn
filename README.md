# EmotionLearn: Real-Time Facial Emotion Recognition & Learning Platform

**EmotionLearn** is a real-time facial emotion recognition and education platform designed to help users understand, express, and identify basic human emotions. Built with **Deep Learning**, **OpenCV**, **Flask**, and **JavaScript**, it bridges the gap between facial emotion recognition technology and interactive learning.

This project is especially useful for:

- Educators and students learning about human emotions
- Individuals with difficulty in emotion interpretation (e.g., ASD support)
- Researchers exploring Human-Computer Interaction
- Developers studying real-time CNN-based facial emotion detection

---

## 🔍 Project Overview

Understanding human emotion is critical for social communication. EmotionLearn is a web-based system that:

- Detects facial emotions using a **CNN trained on FER-2013**
- Teaches emotional features through visuals and sound
- Enables real-time practice with live camera input
- Tests the user’s understanding with a multiple-choice quiz

The tool is modular and offers a friendly interface with three core modules:

1. **Learn About Emotions**
2. **Practice Expressions**
3. **Take a Quiz**

---

## Outputs

### Home Interface
![Home Page](![Image](https://github.com/user-attachments/assets/2b3abf74-8cd1-4506-bce1-b3511d3499eb))

### Learning Module
Explore detailed information on each emotion.
![Learn Page](![Image](https://github.com/user-attachments/assets/cfdbd5da-7dac-4d39-8253-b6b3d4b2b5df))
![Image](https://github.com/user-attachments/assets/8457847a-b0dc-45a3-a33f-354289b13103)

### Quiz Module
Identify emotions shown in various images.
![Quiz Page](![Image](https://github.com/user-attachments/assets/b417d322-6669-4987-969f-494e6b602f8f))
![Image](https://github.com/user-attachments/assets/96b37d79-789a-4c28-b909-967a76040206)

### Practice Module
Practice different emotions in Real time 
![Practice Page](![Image](https://github.com/user-attachments/assets/8dac5948-672e-42fe-a60a-d59561b430fb))
![Image](https://github.com/user-attachments/assets/4eec7cb1-061e-45e0-aac8-b87bfcb37a14)
![Image](https://github.com/user-attachments/assets/0e197965-a427-42d0-a313-f711239d0a2e)

---

## 🧠 Core Features

### 1. Learn About Emotions
Navigate to `/learn` to select and study any of the 7 basic emotions:
- Descriptions of emotional meaning
- Key facial features (e.g., mouth shape, eye tension)
- Sound cues and Text-to-Speech playback for accessibility
- Example images and emojis for visual learners

### 2. Practice Expressions
On the `/practice` page:
- Use your webcam to make expressions
- The system detects your emotion in real-time
- Emotion predictions are stabilized using a smoothing algorithm
- You receive instant feedback through visuals and sound

### 3. Emotion Quiz
The `/quiz` module allows you to:
- Identify emotions from example images
- Choose the correct answer from multiple options
- Receive immediate feedback, explanation, and final score

---

## 🏗️ Technical Architecture

- **Frontend**: HTML/CSS + JavaScript (AJAX for live webcam feed)
- **Backend**: Flask-based API endpoints
- **Model**: CNN trained on FER-2013 with Keras & TensorFlow
- **Face Detection**: Haar Cascade Classifier (OpenCV)
- **Emotion Smoothing**: Maintains recent predictions to ensure stable feedback
- **Multimodal Learning**: Combines sound cues, emoji visuals, and TTS

---

## 📁 Project Structure

```

EmotionLearn/
├── app.py                    # Flask entry point
├── main.py                   # Manages Learn, Practice, Quiz logic
├── emotion\_detector.py       # CNN + Face Detection module
├── templates/                # HTML views (learn.html, quiz.html, etc.)
├── static/                   # CSS, JS, emoji images, and sounds
├── pretrained\_models/        # Folder for the .h5 model file
├── logs/                     # CSV logs of activity
├── requirements.txt          # Python dependencies
└── README.md

````

---

## 📦 Dataset & Model Setup

This project uses the [FER-2013 dataset](https://www.kaggle.com/datasets/msambare/fer2013) and a custom-trained CNN model.

> **Note**: Large files are not included in this repository.

### How to Set It Up:

#### 1. Dataset
- Download from [Kaggle](https://www.kaggle.com/datasets/msambare/fer2013)
- Save `fer2013.csv` in the root directory

#### 2. Trained Model
- The `.h5` model file is either auto-downloaded or you can manually download it
- Place it in the `pretrained_models/` folder

---

## ⚙️ Installation & Running

### Prerequisites
- Python 3.7+
- Webcam
- Google Chrome or any modern browser

### Installation

```bash
git clone https://github.com/man-swi/Emotion-Learn.git
cd Emotion-Learn
python -m venv venv
source venv/bin/activate      # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python app.py
````

Then open your browser and visit:
`http://127.0.0.1:5000`

---

## 🧠 Model Architecture (CNN)

* Input: 48x48 grayscale image
* 4 Convolutional Blocks: Conv2D + BatchNorm + MaxPooling
* Fully connected Dense layer with dropout
* Output: 7-class Softmax (Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise)
* Training enhancements: class weighting, data augmentation

---

## 🔍 Research & Use Case

EmotionLearn is backed by an academic research paper that:

* Reviews prior work on FER and CNNs
* Highlights challenges like dataset bias, real-time fluctuations
* Describes our architecture and smoothing mechanism
* Proposes multimodal learning for inclusive education

> Ideal for integrating into studies on affective computing, HCI, emotional intelligence training, and educational tech.

---

## 📄 License & Attribution

This project is open-source and developed for educational and assistive purposes. See the `LICENSE` file for details.

Developed by:
**Manaswi Kamble**
B.Tech AI & Data Science, VIIT Pune
Email: [manaswi.22211013@viit.ac.in](mailto:manaswi.22211013@viit.ac.in)
