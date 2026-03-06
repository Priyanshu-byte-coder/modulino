"""
Flask web application for the Wellbeing AI Companion.
Provides a browser-based interface accessible on Raspberry Pi.
"""

import logging
import sys
import base64
import json
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
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


@app.route('/api/chat_stream', methods=['POST'])
def chat_stream():
    """Process a chat message and stream the response via SSE."""
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
    
    def generate():
        try:
            if face_emotion:
                yield f"data: {json.dumps({'type': 'emotion', 'emotion': face_emotion})}\n\n"
            
            response_generator = brain.process(user_message, face_emotion=face_emotion, stream=True)
            
            # Check if brain triggered an exercise offer during processing
            if brain._exercise_state.get("pending"):
                exercises = brain.exercise_manager.get_all_exercises()
                yield f"data: {json.dumps({'type': 'exercise_offer', 'exercises': exercises})}\n\n"
                # Consume the text generator so it doesn't leak
                for _ in response_generator:
                    pass
                brain._exercise_state["pending"] = False
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                return
            
            for token in response_generator:
                yield f"data: {json.dumps({'type': 'token', 'token': token})}\n\n"
                
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        except Exception as e:
            logger.error(f"Error processing message stream: {e}", exc_info=True)
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
            
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/camera/snapshot', methods=['GET'])
def camera_snapshot():
    """Capture a single frame from the camera with emotion detection overlay."""
    global camera
    
    if not CAMERA_ENABLED or camera is None:
        return jsonify({"error": "Camera not enabled"}), 400
    
    if not camera.is_available():
        return jsonify({"error": "Camera not initialized. Check webcam connection and permissions."}), 400
    
    try:
        jpeg_bytes, emotion = camera.capture_snapshot_with_overlay()
        if jpeg_bytes is None:
            return jsonify({"error": "Failed to capture frame from webcam"}), 500
        
        jpg_as_text = base64.b64encode(jpeg_bytes).decode('utf-8')
        
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


@app.route('/api/trigger_exercise', methods=['POST'])
def trigger_exercise():
    """Manually trigger an exercise offer (for demos/evaluation)."""
    global brain
    
    if brain is None:
        initialize_agent()
    
    try:
        brain._exercise_state["pending"] = True
        exercises = brain.exercise_manager.get_all_exercises()
        logger.info("Manual exercise trigger activated")
        
        return jsonify({
            "success": True,
            "exercises": exercises
        })
    except Exception as e:
        logger.error(f"Error triggering exercise: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/exercises', methods=['GET'])
def list_exercises():
    """Return the full list of available exercises with step metadata."""
    global brain
    
    if brain is None:
        initialize_agent()
    
    return jsonify({"exercises": brain.exercise_manager.get_all_exercises()})


@app.route('/api/exercise/skip', methods=['POST'])
def skip_exercise():
    """Clear exercise state when user skips via frontend."""
    global brain
    
    if brain is None:
        initialize_agent()
    
    brain._exercise_state["pending"] = False
    brain._exercise_state["active"] = False
    brain._exercise_state["current_exercise"] = None
    logger.info("Exercise skipped via frontend")
    
    return jsonify({"success": True})


@app.route('/api/exercise/start', methods=['POST'])
def start_exercise():
    """Start a specific exercise by name. Returns exercise steps with timer data."""
    global brain
    
    if brain is None:
        initialize_agent()
    
    data = request.json
    exercise_name = data.get("name", "")
    
    exercise = brain.exercise_manager.get_exercise_by_name(exercise_name)
    if exercise is None:
        return jsonify({"error": f"Exercise '{exercise_name}' not found"}), 404
    
    brain._exercise_state["pending"] = False
    brain._exercise_state["active"] = True
    brain._exercise_state["current_exercise"] = exercise
    logger.info(f"Starting exercise: {exercise.name}")
    
    return jsonify({
        "success": True,
        "exercise": exercise.to_dict()
    })


if __name__ == '__main__':
    logger.info("Starting Wellbeing AI Web Application...")
    logger.info("Access the app at: http://localhost:5000")
    logger.info("Or from another device: http://<raspberry-pi-ip>:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
