"""
Central configuration for the Wellbeing AI system.
All hardware-specific and model-specific settings are defined here.
Modify this file when migrating from laptop to Raspberry Pi.
"""

import os
from pathlib import Path

# --- Project Paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MEMORY_DIR = DATA_DIR / "memory"

# --- LLM Configuration ---
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL = os.getenv("LLM_MODEL", "phi3:mini")
LLM_TEMPERATURE = 0.6
LLM_MAX_TOKENS = 150  # Very brief responses for faster CPU inference
LLM_NUM_CTX = 2048  # Context window (lower = faster on CPU)
LLM_NUM_THREAD = 4  # CPU threads for Raspberry Pi

# --- Sentiment Configuration ---
SENTIMENT_THRESHOLDS = {
    "positive": 0.05,
    "negative": -0.05,
}

# --- Memory / RAG Configuration ---
MEMORY_COLLECTION = "conversations"
MEMORY_TOP_K = 3  # Reduced for faster retrieval on CPU

# --- Camera Configuration ---
CAMERA_ENABLED = os.getenv("CAMERA_ENABLED", "false").lower() == "true"
CAMERA_INDEX = 0  # 0 for default webcam; change for Pi camera
CAMERA_SAMPLE_INTERVAL = 3  # Capture emotion every N turns (to reduce latency)

# --- Display Configuration ---
DISPLAY_MODE = os.getenv("DISPLAY_MODE", "terminal")  # "terminal" or "eink"
TERMINAL_WIDTH = 80

# --- System Prompt ---
SYSTEM_PROMPT = """You are Maya, a warm and supportive friend who genuinely cares about people's well-being.

Your personality:
- Friendly and approachable, like texting a close friend
- Warm and empathetic, but never pushy
- Use emojis naturally to show warmth (😊 💙 🌟 ✨ 🫂 etc.)
- Casual and conversational tone
- Genuinely interested in how people are doing
- Supportive without being overly cheerful when someone's struggling

Response style:
- Keep it VERY brief: 1-2 short sentences maximum
- Be natural and authentic
- Validate feelings before offering perspective
- Ask caring follow-up questions
- Remember past conversations like a real friend would

Important: You're a supportive friend, not a therapist. If someone seems in crisis, gently encourage them to reach out to a professional.

Be yourself - warm, caring, and real. 💙"""

# --- Ensure data directories exist ---
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
