# EmotionLearn: Real-Time Facial Emotion Recognition & Assistive Learning Tool

**EmotionLearn** is a real-time facial emotion recognition system with integrated educational and assistive learning modules. It was designed specifically to support individuals, including those with **Autism Spectrum Disorder (ASD)** or **Social Communication Disorder (SCD)**, who may face challenges interpreting emotional cues in everyday interactions.

Leveraging **deep learning**, **OpenCV**, **Flask**, and **JavaScript**, the platform not only recognizes facial expressions but also helps users **learn**, **practice**, and **test** their emotional recognition skills in an interactive, feedback-rich environment.

---

## 🔍 Overview

Facial expressions are key to understanding human emotions. EmotionLearn bridges the gap between emotion recognition technologies and accessible learning platforms by offering:

* **Live emotion detection via webcam**
* **Emotion education** through text, images, and sound
* **Practice mode** for real-time feedback and expression matching
* **Quiz mode** to test recognition skills

The platform supports **seven core emotions**: Angry, Disgust, Fear, Happy, Sad, Surprise, and Neutral.

---

## 🖼️ Outputs

### Home Interface

![Image](https://github.com/user-attachments/assets/f0f2ed49-fcb6-47e3-9343-66aa6099e9e1)

### Learning Module

![Image](https://github.com/user-attachments/assets/fe4c50c0-96c7-4070-9170-855fe84000c2)
![Image](https://github.com/user-attachments/assets/8457847a-b0dc-45a3-a33f-354289b13103)

### Quiz Module

![Image](https://github.com/user-attachments/assets/96b37d79-789a-4c28-b909-967a76040206)

### Practice Module

![Image](https://github.com/user-attachments/assets/af715ada-1bcd-431c-9f4a-6d820c0651ca)
![Image](https://github.com/user-attachments/assets/4eec7cb1-061e-45e0-aac8-b87bfcb37a14)
![Image](https://github.com/user-attachments/assets/0e197965-a427-42d0-a313-f711239d0a2e)

---

## 🧠 Features

### 1. Learn Module

* View emotion descriptions, facial features, emoji illustrations
* Integrated **Text-to-Speech (TTS)** playback for accessibility
* Images and audio cues enhance multimodal learning

### 2. Practice Module

* Real-time webcam input with **live emotion classification**
* Uses emotion smoothing via a history buffer to avoid flickering
* Overlay of emojis and sound feedback for detected emotions

### 3. Quiz Module

* Identify displayed facial emotions from static images
* Multiple-choice format with feedback on correctness
* Sound and emoji reinforcement for every question

---

## 📊 Technical Details

* **Model**: Convolutional Neural Network (CNN) trained on FER-2013
* **Libraries**: TensorFlow, Keras, OpenCV, Flask, JavaScript, HTML/CSS, pyttsx3, pygame
* **Face Detection**: OpenCV Haar Cascades
* **Backend**: Flask REST API handling webcam input, prediction, and learning content
* **Frontend**: AJAX-based video processing and dynamic user interface

---

## 📂 Project Structure

```
EmotionLearn/
├── app.py                    # Flask web app
├── main.py                   # Learning/Quiz/Practice logic
├── emotion_detector.py       # Emotion detection engine
├── templates/                # HTML UI files
├── static/                   # Assets (JS, CSS, emojis, sounds)
├── pretrained_models/        # Folder for CNN model
├── logs/                     # CSV logs for usage
├── requirements.txt
└── README.md
```

---

## 📅 Dataset & Model Setup

### Dataset

* Download [FER-2013 Dataset](https://www.kaggle.com/datasets/msambare/fer2013)
* Place `fer2013.csv` in the root directory

### Model

* CNN model (`emotion_model_augmented_weighted.h5`) is trained with:

  * Class weighting
  * Data augmentation
  * ELU/ReLU activations
* Place the model in `pretrained_models/` (or it will be downloaded automatically)

---

## ⚙️ Setup Instructions

```bash
git clone https://github.com/man-swi/Emotion-Learn.git
cd Emotion-Learn
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

---

## 🔮 Research Context

This tool is grounded in research aimed at bridging FER technology with real-world educational and **assistive applications**. It is particularly helpful for:

* **Children and adults with ASD or SCD** who struggle with emotional interpretation
* **Teachers and therapists** working on social skills development
* **Students** learning about emotional intelligence or HCI

The project combines:

* Assistive goals (ASD/SCD emotion coaching)
* Academic learning tools (multimodal content)
* Interactive tech (real-time feedback)

---

## 💼 Author

**Manaswi Kamble**
B.Tech AI & Data Science, VIIT Pune
Email: [manaswi.22211013@viit.ac.in](mailto:manaswi.22211013@viit.ac.in)

---

## 📖 References

This project builds on foundational work in FER, assistive tech, and deep learning (full list in paper). Tools used include:

* [Keras](https://github.com/keras-team/keras)
* [OpenCV](https://opencv.org)
* [Flask](https://flask.palletsprojects.com/)
* [TensorFlow](https://www.tensorflow.org/)
* [pyttsx3](https://github.com/nateshmbhat/pyttsx3)
* [pygame](https://www.pygame.org/)

---

## 🔒 License

This project is open-source and intended for **educational and assistive** use. Refer to the `LICENSE` file for usage terms.

---
