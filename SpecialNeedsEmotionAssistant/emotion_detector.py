import cv2
import numpy as np
from tensorflow.keras.models import load_model
import os
import traceback  

class EmotionDetector:
    def __init__(self, padding_ratio=0.1, confidence_threshold=0.30):
        self.padding_ratio = padding_ratio
        self.confidence_threshold = confidence_threshold
        self.emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
        print(f"Emotion Detector initialized with confidence_threshold={self.confidence_threshold}")


        script_dir = os.path.dirname(os.path.abspath(__file__))
        if os.path.basename(script_dir) == 'SpecialNeedsEmotionAssistant':
            app_root = os.path.dirname(script_dir)
        else:
            app_root = script_dir 
        self.model_filename = 'emotion_model_augmented_weighted.h5'
     
        model_path = os.path.join(app_root, 'pretrained_models', self.model_filename)

        print(f"Attempting to load model from: {model_path} (App root: {app_root})")

        if os.path.exists(model_path):
            try:
               
                self.model = load_model(model_path)
                print(f"Emotion model loaded successfully from: {model_path}")
            except Exception as e:
                print(f"FATAL ERROR: Failed to load Keras model from {model_path}. Error: {e}")
                traceback.print_exc()
                raise  
        else:
            print(f"FATAL ERROR: Emotion model '{self.model_filename}' not found at expected path: {model_path}")
           
            print(f"Contents of {app_root}: {os.listdir(app_root)}")
            pretrained_path = os.path.join(app_root, 'pretrained_models')
            if os.path.exists(pretrained_path):
                print(f"Contents of {pretrained_path}: {os.listdir(pretrained_path)}")
            else:
                print(f"{pretrained_path} directory NOT found.")
            raise FileNotFoundError(f"Emotion model '{self.model_filename}' not found at {model_path}")

        print(f"Emotion labels used by detector: {self.emotion_labels}")

        haar_cascade_filename = 'haarcascade_frontalface_default.xml'
      
        cascade_path = os.path.join(app_root, haar_cascade_filename)

        print(f"Attempting to load Haar cascade from: {cascade_path}")

        if os.path.exists(cascade_path):
            try:
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
                if self.face_cascade.empty():
                    raise IOError(f"Failed to load cascade classifier from {cascade_path}, but file exists.")
                print(f"Face cascade classifier loaded successfully from: {cascade_path}")
            except Exception as e:
                print(f"FATAL ERROR: Error loading Haar cascade file from {cascade_path}: {e}")
                traceback.print_exc()
                raise 
        else:
            opencv_cascade_path = os.path.join(cv2.data.haarcascades, haar_cascade_filename)
            print(f"Cascade not found at {cascade_path}, trying standard OpenCV path: {opencv_cascade_path}")
            if os.path.exists(opencv_cascade_path):
                try:
                    self.face_cascade = cv2.CascadeClassifier(opencv_cascade_path)
                    if self.face_cascade.empty():
                        raise IOError(f"Failed to load cascade classifier from {opencv_cascade_path}, but file exists.")
                    print(f"Face cascade classifier loaded successfully from standard path: {opencv_cascade_path}")
                except Exception as e:
                    print(f"FATAL ERROR: Error loading Haar cascade file from standard path {opencv_cascade_path}: {e}")
                    traceback.print_exc()
                    raise  
            else:
                print(f"FATAL ERROR: Haar cascade file '{haar_cascade_filename}' not found.")
                print(f"Checked paths: {cascade_path} (Exists: {os.path.exists(cascade_path)}), {opencv_cascade_path} (Exists: {os.path.exists(opencv_cascade_path)})")
                raise FileNotFoundError(f"Haar cascade file '{haar_cascade_filename}' not found in checked locations.")

    def detect_emotion(self, frame):
        """
        Detects faces, predicts emotions using the loaded model, applies
        confidence threshold (defaulting to Neutral), and returns results.

        Args:
            frame: The input BGR frame from the webcam.

        Returns:
            A list of tuples [((x, y, w, h), final_label, confidence)] for all detected faces.
            'final_label' will be the predicted emotion if confidence >= threshold,
            otherwise it will be 'Neutral'.
        """
        detected_results = []
        if frame is None or frame.size == 0:
            return []

        try:
        
            gray_orig = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            orig_height, orig_width = gray_orig.shape[:2]
            if orig_width <= 0 or orig_height <= 0:
                return [] 

           
            faces = self.face_cascade.detectMultiScale(
                gray_orig, scaleFactor=1.1, minNeighbors=5, minSize=(40, 40)
            )

          
            for (x, y, w, h) in faces:
             
                pad_w = int(w * self.padding_ratio)
                pad_h = int(h * self.padding_ratio)
                y1 = max(0, y - pad_h)
                y2 = min(orig_height, y + h + pad_h)
                x1 = max(0, x - pad_w)
                x2 = min(orig_width, x + w + pad_w)
                roi_gray_padded = gray_orig[y1:y2, x1:x2]
                if roi_gray_padded.size == 0:
                    continue

                try:
                    roi_gray_resized = cv2.resize(roi_gray_padded, (48, 48), interpolation=cv2.INTER_AREA)
                except cv2.error as e:
                    print(f"Warning: cv2.resize error on ROI: {e}")
                    continue 

                roi_processed = roi_gray_resized.astype('float32') / 255.0
                roi_processed = np.expand_dims(roi_processed, axis=-1)
                roi_processed = np.expand_dims(roi_processed, axis=0)

                
                try:
                    predictions = self.model.predict(roi_processed, verbose=0)
                except Exception as pred_err:
                    print(f"Error during model prediction: {pred_err}")
                    final_label = "Error"
                    confidence = 0.0
                    face_box = (x, y, w, h)
                    detected_results.append((face_box, final_label, confidence))
                    continue 

                confidence = np.max(predictions[0])
                emotion_index = np.argmax(predictions[0])

                if emotion_index >= len(self.emotion_labels):
                    print(f"Warning: Predicted index {emotion_index} out of bounds for labels {self.emotion_labels}. Defaulting to Neutral.")
                    predicted_label = "Neutral"
                else:
                    predicted_label = self.emotion_labels[emotion_index]

                if confidence >= self.confidence_threshold:
                    final_label = predicted_label
                else:
                    final_label = "Neutral"

                face_box = (x, y, w, h)
                detected_results.append((face_box, final_label, confidence))

            return detected_results

        except cv2.error as e:
            print(f"OpenCV Error during detection: {e}")
            traceback.print_exc()
            return []
        except AttributeError as e:
            print(f"Attribute Error (model/cascade likely not loaded): {e}")
            traceback.print_exc()
            raise
        except Exception as e:
            print(f"General Error during emotion detection: {type(e).__name__}: {e}")
            traceback.print_exc()
            return []