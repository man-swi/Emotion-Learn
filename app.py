from flask import Flask, jsonify, render_template, request, url_for
import sys
import os
import base64
import numpy as np
import cv2
import time
import atexit

script_dir = os.path.dirname(os.path.abspath(__file__))
sna_path = os.path.join(script_dir, 'SpecialNeedsEmotionAssistant')
if sna_path not in sys.path:
    sys.path.insert(0, sna_path)

try:
   
    from main import EmotionLearningTool
except ImportError as e:
    print(f"ERROR: Could not import EmotionLearningTool from {os.path.join(sna_path, 'main.py')}")
    print(f"Check that the file exists and contains the class. Current sys.path includes: {sys.path}")
    print(f"Error: {e}")
    sys.exit(1)
except FileNotFoundError as e:

    print(f"ERROR: Could not find main.py in {sna_path}")
    sys.exit(1)

app = Flask(__name__,
        
            static_folder=os.path.join(sna_path, 'assets'),
            template_folder='templates')


CONFIDENCE_THRESHOLD_FOR_DETECTOR = 0.25 
SMOOTHING_HISTORY_LENGTH = 7     

print("Initializing backend tool...")
try:
    learning_tool = EmotionLearningTool(
        confidence_threshold=CONFIDENCE_THRESHOLD_FOR_DETECTOR,
        history_len=SMOOTHING_HISTORY_LENGTH
        )
except FileNotFoundError as e:
    
     print(f"FATAL ERROR: Failed to initialize EmotionLearningTool - Required file not found: {e}")
     sys.exit(1)
except Exception as e:
    print(f"FATAL ERROR: Failed to initialize EmotionLearningTool: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
print(f"Backend tool initialized with confidence_threshold={CONFIDENCE_THRESHOLD_FOR_DETECTOR}, history_len={SMOOTHING_HISTORY_LENGTH}.")

@app.route('/')
def index():
    """Renders the home page."""
    return render_template('index.html')

@app.route('/learn')
def learn_page():
    """Renders the learning page, passing available emotions."""
   
    emotions = sorted(list(learning_tool.learning_content.keys()))
    return render_template('learn.html', emotions=emotions)

@app.route('/practice')
def practice_page():
    """Renders the practice page."""
    return render_template('practice.html')

@app.route('/quiz')
def quiz_page():
    """Renders the quiz page."""
    return render_template('quiz.html')

@app.route('/api/learn_data/<emotion_name>')
def api_get_learn_data(emotion_name):
    """Gets learning content (desc, features, images) for a specific emotion."""
    data = learning_tool.get_learn_data(emotion_name)
    try:
        
        if 'emoji_path' in data and data['emoji_path']:
             data['emoji_url'] = url_for('static', filename=data['emoji_path'])
        if 'image_paths' in data and data['image_paths']:
            data['image_urls'] = [url_for('static', filename=p) for p in data['image_paths']]
    except Exception as e:
        print(f"Error generating static URLs in learn_data for {emotion_name}: {e}")
    return jsonify(data)

@app.route('/api/quiz_question')
def api_get_quiz_question():
    """Gets data for a new quiz question."""
    data = learning_tool.get_quiz_question()
    try:
        if 'image_path' in data and data['image_path']:
            data['image_url'] = url_for('static', filename=data['image_path'])
    except Exception as e:
        print(f"Error generating static URL for quiz image: {e}")
    return jsonify(data)



@app.route('/api/check_answer', methods=['POST'])
def api_check_quiz_answer():
    """Checks a submitted quiz answer and adds emoji URL."""
    data = request.get_json()
    if not data or 'chosen_answer' not in data or 'correct_answer' not in data:
        return jsonify({"error": "Missing data for checking answer"}), 400

    result = learning_tool.check_quiz_answer(data['chosen_answer'], data['correct_answer'])

    try:
        if 'correct_emoji_path' in result and result['correct_emoji_path']:
            result['correct_emoji_url'] = url_for('static', filename=result['correct_emoji_path'])
        else:
            result['correct_emoji_url'] = None
    except Exception as e:
        print(f"Error generating correct emoji URL for quiz feedback: {e}")
        result['correct_emoji_url'] = None


    return jsonify(result) 

@app.route('/api/process_frame', methods=['POST'])
def api_process_practice_frame():
    """Receives a frame, processes it for emotion, returns smoothed result."""
    data = request.get_json()
    if not data or 'imageData' not in data:
        return jsonify({"error": "Missing image data"}), 400

    try:
   
        header, encoded = data['imageData'].split(",", 1)
        image_data_decoded = base64.b64decode(encoded)
        np_arr = np.frombuffer(image_data_decoded, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if frame is None:
            raise ValueError("Could not decode image")
    except Exception as e:
        print(f"Error decoding image data: {e}")
        return jsonify({"error": f"Error decoding image: {e}"}), 400

    result = learning_tool.process_practice_frame(frame) 

   
    try:
        if 'emotion' in result and result['emotion'] and 'emoji_path' in result and result['emoji_path']:
            result['emoji_url'] = url_for('static', filename=result['emoji_path'])
    except Exception as e:
        print(f"Error generating emoji URL for practice result: {e}")
        result.pop('emoji_url', None) 
    return jsonify(result)

@app.route('/api/play_sound/<emotion_name>')
def api_play_sound(emotion_name):
    """Triggers the backend to play the sound cue for an emotion."""
    if 'learning_tool' in globals():
        result = learning_tool.play_sound(emotion_name)
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "Backend tool not initialized"}), 500


@app.route('/api/speak_description/<emotion_name>')
def api_speak_description(emotion_name):
    """Triggers the backend to speak the description of the given emotion."""
    if 'learning_tool' in globals():
        result = learning_tool.speak_description(emotion_name)
        return jsonify(result)
    else:
        return jsonify({"status": "error", "message": "Backend tool not initialized"}), 500

def shutdown_server():
    """Function called when the Flask server is shutting down."""
    print("Flask server shutting down, calling backend tool shutdown...")
    if 'learning_tool' in globals():
        learning_tool.shutdown() 
    print("Flask shutdown actions complete.")

atexit.register(shutdown_server)

if __name__ == '__main__':
    print("Starting Flask server for Emotion Learning Tool...")
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)