"""
Flask web application for the Wellbeing AI Companion.
Provides a browser-based interface accessible on Raspberry Pi.
"""

import logging
import sys
import base64
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
import cv2

from agent.brain import AgentBrain
from interface.camera import create_camera
from config.config import CAMERA_ENABLED, OLLAMA_BASE_URL, LLM_MODEL

app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)

brain = None
camera = None
turn_count = 0


def initialize_agent():
    """Initialize the AI agent and camera."""
    global brain, camera
    
    logger.info("Initializing AI agent...")
    brain = AgentBrain()
    camera = create_camera()
    
    status = brain.check_systems()
    status["camera"] = camera.is_available() if CAMERA_ENABLED else False
    
    logger.info(f"System status: {status}")
    return status


@app.route('/')
def index():
    """Serve the main chat interface."""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Check system status."""
    global brain, camera
    
    if brain is None:
        status = initialize_agent()
    else:
        status = brain.check_systems()
        status["camera"] = camera.is_available() if CAMERA_ENABLED else False
    
    return jsonify({
        "status": status,
        "camera_enabled": CAMERA_ENABLED,
        "ollama_url": OLLAMA_BASE_URL,
        "model": LLM_MODEL
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Process a chat message."""
    global brain, camera, turn_count
    
    if brain is None:
        initialize_agent()
    
    data = request.json
    user_message = data.get('message', '').strip()
    capture_emotion = data.get('capture_emotion', False)
    
    if not user_message:
        return jsonify({"error": "Empty message"}), 400
    
    turn_count += 1
    face_emotion = None
    
    if capture_emotion and CAMERA_ENABLED and camera.is_available():
        logger.info("Capturing emotion from camera...")
        face_emotion = camera.capture_emotion()
        logger.info(f"Detected emotion: {face_emotion}")
    
    try:
        response = brain.process(user_message, face_emotion=face_emotion)
        
        return jsonify({
            "response": response,
            "face_emotion": face_emotion,
            "turn_count": turn_count
        })
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/camera/snapshot', methods=['GET'])
def camera_snapshot():
    """Capture a single frame from the camera with emotion detection overlay."""
    global camera
    
    if not CAMERA_ENABLED or camera is None:
        return jsonify({"error": "Camera not enabled"}), 400
    
    if not camera._initialized or camera._cap is None:
        return jsonify({"error": "Camera not initialized. Check webcam connection and permissions."}), 400
    
    try:
        # Capture frame
        ret, frame = camera._cap.read()
        if not ret or frame is None:
            return jsonify({"error": "Failed to capture frame from webcam"}), 500
        
        # Detect emotion
        emotion = None
        try:
            if camera._detector is not None:
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = camera._detector.detect_emotions(rgb_frame)
                
                if result and len(result) > 0:
                    emotions = result[0]["emotions"]
                    emotion = max(emotions, key=emotions.get)
                    confidence = emotions[emotion]
                    
                    # Draw bounding box and emotion label on frame
                    box = result[0]["box"]
                    x, y, w, h = box
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    
                    # Add emotion text with background
                    text = f"{emotion}: {confidence:.2f}"
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text_size = cv2.getTextSize(text, font, 0.6, 2)[0]
                    cv2.rectangle(frame, (x, y-30), (x+text_size[0]+10, y), (0, 255, 0), -1)
                    cv2.putText(frame, text, (x+5, y-10), font, 0.6, (0, 0, 0), 2)
        except Exception as e:
            logger.warning(f"Emotion detection failed: {e}")
        
        # Encode frame to JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        jpg_as_text = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            "image": f"data:image/jpeg;base64,{jpg_as_text}",
            "emotion": emotion
        })
    except Exception as e:
        logger.error(f"Error capturing snapshot: {e}", exc_info=True)
        return jsonify({"error": f"Camera error: {str(e)}"}), 500


@app.route('/api/camera/emotion', methods=['GET'])
def detect_emotion():
    """Detect emotion from current camera frame."""
    global camera
    
    if not CAMERA_ENABLED or camera is None or not camera.is_available():
        return jsonify({"error": "Camera not available"}), 400
    
    try:
        emotion = camera.capture_emotion()
        return jsonify({
            "emotion": emotion,
            "success": emotion is not None
        })
    except Exception as e:
        logger.error(f"Error detecting emotion: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history."""
    global brain, turn_count
    
    if brain:
        brain._conversation_history = []
        turn_count = 0
        logger.info("Conversation reset")
    
    return jsonify({"success": True})


if __name__ == '__main__':
    logger.info("Starting Wellbeing AI Web Application...")
    logger.info("Access the app at: http://localhost:5000")
    logger.info("Or from another device: http://<raspberry-pi-ip>:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
