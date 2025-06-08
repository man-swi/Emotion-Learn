# --- START OF FILE SpecialNeedsEmotionAssistant/main.py ---

import cv2
import time
import pandas as pd
from pygame import mixer
try:
    from emotion_detector import EmotionDetector
except ImportError:
    print("ERROR: Cannot find emotion_detector.py in the same folder as main.py")
    import sys 
    sys.exit(1)
import pyttsx3
import os
import threading
from collections import deque
import sys
import random
import json 
import numpy as np

class EmotionLearningTool:
    """
    Provides backend logic for an emotion learning web application.
    Manages resources and provides methods for learning, practice, and quizzes.
    Includes backend smoothing for practice mode detections.
    """
    def __init__(self, confidence_threshold=0.25, history_len=7): 
        print("Initializing Emotion Learning Tool Backend...")
        self.detector = None
        self.engine = None
        self.sounds = {}
        self.emojis = {}
        self.learning_content = {}

        self.confidence_threshold = confidence_threshold
        self.padding_ratio = 0.1
        self.history_len = history_len 

        self.prediction_history = deque(maxlen=self.history_len)
        self.last_stable_emotion = 'Neutral'

     
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.assets_path = os.path.join(self.script_dir, 'assets')
        self.project_root = os.path.dirname(self.script_dir)
        self.log_dir = os.path.join(self.project_root, 'logs')
        self.log_path = os.path.join(self.log_dir, 'learning_tool_log.csv')

        
        self._load_detector()
        self._load_assets() 
        self._initialize_mixer()
        self._initialize_tts()
        self._load_learning_content()

  
        self.log = []
        os.makedirs(self.log_dir, exist_ok=True)
        print(f"Log file will be saved to: {self.log_path}")
        print("Emotion Learning Tool Backend Initialized Successfully.")

    def _load_detector(self):
        try:
            self.detector = EmotionDetector(
                padding_ratio=self.padding_ratio,
                confidence_threshold=self.confidence_threshold 
            )
           
            if not hasattr(self.detector, 'model_filename'):
                
                 self.detector.model_filename = "emotion_model_augmented_weighted.h5"
            print(f"Emotion Detector loaded using model: {self.detector.model_filename}")
        except FileNotFoundError as e: print(f"FATAL ERROR loading detector: {e}"); raise
        except Exception as e: print(f"FATAL ERROR loading detector: {e}"); raise

    def _initialize_mixer(self):
        try:
            mixer.init()
            print("Pygame mixer initialized.")
            self._load_sounds()
        except Exception as e:
            print(f"Warning: Pygame mixer init failed: {e}. Sounds disabled.")
            self.sounds = {} 

    def _initialize_tts(self):
        try:
            self.engine = pyttsx3.init()
            print("TTS engine initialized.")
        except Exception as e:
            print(f"Warning: TTS init failed: {e}. TTS disabled.")
            self.engine = None

    def _load_assets(self):
        """Loads emoji assets."""
        emoji_folder = os.path.join(self.assets_path, 'emojis')
        self.emojis = {}
        
        if not self.detector:
             print("Error: Detector not loaded before loading assets. Cannot get emotion labels.")
             all_possible_emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'] # Fallback
        else:
             all_possible_emotions = getattr(self.detector, 'emotion_labels', ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'])

        print("Loading emojis...")
        for emotion in all_possible_emotions:
            filename = f"{emotion.lower()}.png"
            path = os.path.join(emoji_folder, filename)
            if os.path.exists(path):
                 
                 self.emojis[emotion] = os.path.join('emojis', filename).replace('\\', '/')
           
        print(f"Registered emojis for: {list(self.emojis.keys())}")


    def _load_sounds(self):
        """Loads sound cue assets."""
        if not mixer.get_init():
            print("Info: Mixer not initialized, skipping sound loading.")
            return 

        sound_folder = os.path.join(self.assets_path, 'sounds')
        self.sounds = {}

        if not self.detector:
             print("Error: Detector not loaded before loading sounds. Cannot get emotion labels.")
             all_possible_emotions = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'] # Fallback
        else:
            all_possible_emotions = getattr(self.detector, 'emotion_labels', ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'])

       
        sound_mapping = {'Neutral': 'neutral.mp3'} 

        print("Loading sounds...")
        for emotion in all_possible_emotions:
            filename = sound_mapping.get(emotion, f"{emotion.lower()}.mp3")
            path = os.path.join(sound_folder, filename)
            if os.path.exists(path):
                try:
                     self.sounds[emotion] = mixer.Sound(path)
                except Exception as e:
                     print(f"Warning: Could not load sound '{path}' for {emotion}. Error: {e}")
           
        print(f"Loaded sounds for: {list(self.sounds.keys())}")

    def _load_learning_content(self):
        """Loads descriptions, key features, and associated images."""
        print("Loading learning content...")
        content_base = os.path.join(self.assets_path, 'learning_content')
        images_base = os.path.join(content_base, 'images')
        desc_path = os.path.join(content_base, 'descriptions.json')
        descriptions_data = {} 

        if os.path.exists(desc_path):
            try:
             
                with open(desc_path, 'r', encoding='utf-8') as f:
                    descriptions_data = json.load(f)
                print("Loaded descriptions.json")
            except Exception as e:
                print(f"Warning: Could not load descriptions.json: {e}")

        self.learning_content = {}
        emotions_with_folders = []
        if os.path.isdir(images_base):
            emotions_with_folders = [d for d in os.listdir(images_base) if os.path.isdir(os.path.join(images_base, d))]

        if not emotions_with_folders:
            print("Warning: No learning content image subfolders found.")
           

        print(f"Found potential content folders: {emotions_with_folders}")
        if not self.detector:
             print("Error: Detector not loaded before loading learning content. Cannot get emotion labels.")
             model_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'] 
        else:
             model_labels = getattr(self.detector, 'emotion_labels', ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral'])

        
        for emotion in model_labels:
            emotion_data = descriptions_data.get(emotion, {})
            description_text = emotion_data.get("description", f"This is {emotion}.") 
            key_features_list = emotion_data.get("key_features", [])

            image_paths = []
            emotion_image_folder = os.path.join(images_base, emotion)
          
            if os.path.isdir(emotion_image_folder):
                for img_file in os.listdir(emotion_image_folder):
                    if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                        
                        image_paths.append(os.path.join('learning_content/images', emotion, img_file).replace('\\','/'))

  
            self.learning_content[emotion] = {
                "name": emotion,
                "description": description_text,
                "key_features": key_features_list,
                "image_paths": image_paths,
                "emoji_path": self.emojis.get(emotion),
                "sound_available": emotion in self.sounds
            }

        print(f"Loaded learning content for: {list(self.learning_content.keys())}")

    def get_learn_data(self, emotion_name):
        """Retrieves learning data (desc, features, images, etc.) for an emotion."""
        if emotion_name in self.learning_content:
          
            return self.learning_content[emotion_name]
        else:
           
            return {"error": f"Emotion '{emotion_name}' not found in loaded content."}

    def get_quiz_question(self):
        """Generates data for a multiple-choice quiz question."""
        
        available_emotions = [e for e, data in self.learning_content.items() if data.get("image_paths")]

        if not available_emotions:
            return {"error": "No learning content with images available for quiz."}

        correct_emotion = random.choice(available_emotions)
        content = self.learning_content[correct_emotion]
       
        image_path = random.choice(content["image_paths"])


        options = [correct_emotion]
        all_possible_emotions = list(self.learning_content.keys()) 
        distractors = [e for e in all_possible_emotions if e != correct_emotion]

        num_distractors = min(3, len(distractors)) 
        options.extend(random.sample(distractors, num_distractors))
        random.shuffle(options)

        return {
            "image_path": image_path,
            "options": options,
            "correct_answer": correct_emotion
        }


    def check_quiz_answer(self, chosen_answer, correct_answer):
        """Checks if the chosen quiz answer is correct and returns feedback data."""
        is_correct = (chosen_answer == correct_answer)
        self.log_event('quiz_attempt', {'chosen': chosen_answer, 'correct': correct_answer, 'result': is_correct})

        
        sound_available = correct_answer in self.sounds
        correct_emoji_path = self.emojis.get(correct_answer) 

        return {
            "is_correct": is_correct,
            "correct_answer": correct_answer,
            "sound_available": sound_available,
            "correct_emoji_path": correct_emoji_path
        }

    def process_practice_frame(self, frame_data):
        """Processes a frame for practice mode, applying smoothing."""
        if self.detector is None: return {"error": "Detector not loaded."}
        if frame_data is None or not isinstance(frame_data, np.ndarray) or frame_data.size == 0:
            return {"error": "Invalid frame data received."}

        raw_emotion_label = None
        smoothed_emotion = self.last_stable_emotion 

        try:
            detection_results = self.detector.detect_emotion(frame_data)

            if detection_results:
        
                _box, raw_emotion_label, _confidence = detection_results[0]
                self.prediction_history.append(raw_emotion_label)
            else:
                
                self.prediction_history.append(None) 

            
            valid_history = [e for e in self.prediction_history if e is not None]

           
            if len(valid_history) >= max(2, self.history_len // 2 + 1): 
                 try:
                     
                     smoothed_emotion = max(set(valid_history), key=valid_history.count)
                 except ValueError:
                   
                     smoothed_emotion = self.last_stable_emotion
            else:
                 smoothed_emotion = self.last_stable_emotion

            self.last_stable_emotion = smoothed_emotion

            result = {
                'emotion': smoothed_emotion,
                'emoji_path': self.emojis.get(smoothed_emotion),
                'sound_available': smoothed_emotion in self.sounds
            }
            self.log_event('practice_detection_smoothed', {'raw': raw_emotion_label, 'smoothed': smoothed_emotion})
            return result

        except Exception as e:
            print(f"Error during practice frame processing: {e}"); import traceback; traceback.print_exc()
          
            return {
                'emotion': self.last_stable_emotion,
                'emoji_path': self.emojis.get(self.last_stable_emotion),
                'sound_available': self.last_stable_emotion in self.sounds,
                'error': f"Processing error occurred"
            }

    def play_sound(self, emotion_name):
        """Plays the loaded sound cue for the given emotion."""
        if mixer.get_init() and isinstance(emotion_name, str) and emotion_name in self.sounds:
            try:
                mixer.stop() # Stop any currently playing sound
                self.sounds[emotion_name].play()
                print(f"Played sound for {emotion_name}")
                self.log_event('play_sound', {'emotion': emotion_name})
                return {"status": "success", "message": f"Played sound for {emotion_name}"}
            except Exception as e:
                print(f"Error playing sound for {emotion_name}: {e}")
                return {"status": "error", "message": f"Error playing sound: {e}"}
        elif not mixer.get_init():
            return {"status": "error", "message": "Mixer not initialized"}
        elif not isinstance(emotion_name, str):
             return {"status": "error", "message": "Invalid emotion name type"}
        else:
            return {"status": "warning", "message": f"No sound loaded for {emotion_name}"}

    def speak_description(self, emotion_name):
        """Uses the TTS engine to speak the description of an emotion."""
        if not self.engine:
            return {"status": "error", "message": "TTS engine not initialized."}

        if emotion_name in self.learning_content:
            description = self.learning_content[emotion_name].get("description")
            if description:
                try:
                    self.engine.say(description)
                    thread = threading.Thread(target=self._run_tts_engine)
                    thread.daemon = True 
                    thread.start()
                    print(f"Speaking description for {emotion_name}")
                    self.log_event('speak_description', {'emotion': emotion_name})
                    return {"status": "success", "message": f"Speaking description for {emotion_name}."}
                except Exception as e:
                    print(f"Error during TTS processing for {emotion_name}: {e}")
                    return {"status": "error", "message": f"TTS engine error: {e}"}
            else:
                return {"status": "warning", "message": f"No description found for {emotion_name}."}
        else:
            return {"status": "error", "message": f"Emotion '{emotion_name}' not found in learning content."}

    def _run_tts_engine(self):
        """Helper function to run the blocking TTS call in a separate thread."""
        try:
            self.engine.runAndWait()
            print("TTS runAndWait completed.")
        except RuntimeError as e:
            
             print(f"TTS Runtime error in thread: {e}")
        except Exception as e:
             print(f"Generic error in TTS thread: {e}")

    def log_event(self, event_type, data):
        """Adds an event to the internal log list."""
        try:
            serializable_data = json.loads(json.dumps(data, default=str))
            log_entry = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'event_type': event_type,
                'data': serializable_data
            }
            self.log.append(log_entry)
        except Exception as e:
            print(f"Error preparing log entry: {e}")

    def save_log(self):
        """Saves the internal log list to a CSV file."""
        if not self.log:
            print("No new log entries to save.")
            return

        print("Saving log file...")
        try:
            log_df = pd.DataFrame(self.log)
            os.makedirs(self.log_dir, exist_ok=True)
            write_header = not os.path.exists(self.log_path)
            log_df.to_csv(self.log_path, index=False, mode='a', header=write_header)
            print(f"Log data saved to {self.log_path}")
            self.log = [] 
        except Exception as e:
            print(f"Error saving log file: {e}")

    def shutdown(self):
        """Cleans up resources (mixer, save logs)."""
        print("Shutting down Emotion Learning Tool Backend...")
        if self.engine:
            try:
                self.engine.stop() 
            except Exception as e:
                print(f"Error stopping TTS engine: {e}")
        if mixer.get_init():
            try:
                mixer.quit()
                print("Pygame mixer quit.")
            except Exception as e:
                 print(f"Error quitting mixer: {e}")
        self.save_log()
        print("Backend shutdown complete.")

if __name__ == "__main__":
    print("Running main.py directly for testing...")
    try:
        tool_confidence = 0.25
        tool_history = 7
        learning_tool = EmotionLearningTool(confidence_threshold=tool_confidence, history_len=tool_history)

        print("\n--- Testing get_learn_data ---")
        happy_data = learning_tool.get_learn_data('Happy')
        print(f"Happy Data: {json.dumps(happy_data, indent=2)}")

        print("\n--- Testing speak_description (will run in background) ---")
        learning_tool.speak_description('Happy')
        time.sleep(3) 

        print("\n--- Direct Test Sequence Complete ---")
        
        learning_tool.shutdown()

    except FileNotFoundError as e:
        print(f"\nInitialization failed - File Not Found: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during direct test: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)