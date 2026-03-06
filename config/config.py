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
LLM_TEMPERATURE = 0.3  # Lower for more focused, faster responses
LLM_MAX_TOKENS = 60  # Brief responses optimized for CPU
LLM_NUM_CTX = 1024  # Optimized context window for CPU inference
LLM_NUM_THREAD = 4  # CPU threads for Raspberry Pi
LLM_TIMEOUT = 300  # 5 min timeout for slow CPU inference
LLM_STOP_SEQUENCES = ["\n\n", "User:", "Assistant:"]  # Stop at natural breaks

# --- Sentiment Configuration ---
SENTIMENT_THRESHOLDS = {
    "positive": 0.05,
    "negative": -0.05,
}

# --- Memory / RAG Configuration ---
MEMORY_COLLECTION = "conversations"
MEMORY_TOP_K = 2  # Reduced for faster retrieval on CPU

# --- Camera Configuration ---
# CAMERA_ENABLED = os.getenv("CAMERA_ENABLED", "false").lower() == "true"
CAMERA_ENABLED = True
CAMERA_INDEX = 0  # USB webcam capture device (video1 is metadata only)
CAMERA_SAMPLE_INTERVAL = 3  # Capture emotion every N turns (to reduce latency)

# --- Display Configuration ---
DISPLAY_MODE = os.getenv("DISPLAY_MODE", "terminal")  # "terminal" or "eink"
TERMINAL_WIDTH = 80

# --- System Prompt (kept short for CPU performance) ---
SYSTEM_PROMPT = """Your name is Maya. You are an AI wellbeing companion. The human talking to you is the USER — never call them Maya or any made-up name. If you don't know their name, just say "friend" or ask. Never invent a name for the user. You are ALWAYS Maya, the assistant. Keep replies brief (1-2 sentences), warm, and supportive."""

# --- Mental Exercise Configuration ---
EXERCISE_TRIGGER_THRESHOLD = -0.3  # Trigger exercises when sentiment avg drops below this
EXERCISE_COOLDOWN_TURNS = 5  # Don't offer exercises more than once per N turns

# --- Ensure data directories exist ---
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
