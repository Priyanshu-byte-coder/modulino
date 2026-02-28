"""
Wellbeing AI Companion — Main Entry Point.
Runs the conversational loop connecting all modules.
"""

import logging
import sys

from agent.brain import AgentBrain
from interface.display import create_display
from interface.camera import create_camera
from config.config import CAMERA_ENABLED, CAMERA_SAMPLE_INTERVAL


def setup_logging():
    """Configure logging to stderr so it doesn't interfere with terminal UI."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
    )


def main():
    setup_logging()
    logger = logging.getLogger("main")

    display = create_display()
    camera = create_camera()

    display.clear()
    display.show_welcome()

    # Initialize agent
    display.show_status("Initializing AI systems...")
    brain = AgentBrain()

    # System check
    status = brain.check_systems()
    status["camera"] = camera.is_available() if CAMERA_ENABLED else False
    
    for system_name, ok in status.items():
        icon = "✓" if ok else "✗"
        display.show_status(f"  {system_name}: {icon}")

    if not status["llm"]:
        print("\n  [!] Ollama is not running or model not found.")
        print("  Please start Ollama and pull the model:")
        print("      ollama serve")
        print(f"      ollama pull {brain.llm.model}")
        print()
        return

    if CAMERA_ENABLED and status["camera"]:
        print(f"  📷 Camera emotion detection active (sampling every {CAMERA_SAMPLE_INTERVAL} turns)")
    elif CAMERA_ENABLED and not status["camera"]:
        print("  ⚠️  Camera enabled but not available")
    
    print()  # spacing after status

    # Main conversation loop
    turn_count = 0
    while True:
        try:
            user_input = input("  You > ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "bye"):
            display.show_message(
                "assistant", "Take care! I'm always here whenever you need to talk. 💙"
            )
            break

        turn_count += 1

        # Capture facial emotion (if camera enabled and sampling interval reached)
        face_emotion = None
        if CAMERA_ENABLED and status["camera"] and (turn_count % CAMERA_SAMPLE_INTERVAL == 0):
            display.show_status("Capturing emotion from camera...")
            face_emotion = camera.capture_emotion()
            if face_emotion:
                display.show_emotion(face_emotion)
            else:
                print("  ⚠️  No emotion detected (check camera, lighting, or face visibility)")

        display.show_status("Thinking...")
        response = brain.process(user_input, face_emotion=face_emotion)
        display.show_message("assistant", response)

    camera.release()
    logger.info("Session ended.")


if __name__ == "__main__":
    main()
