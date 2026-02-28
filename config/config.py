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
LLM_MODEL = os.getenv("LLM_MODEL", "tinyllama")
LLM_TEMPERATURE = 0.5
LLM_MAX_TOKENS = 50  # Very brief responses for fast CPU inference
LLM_NUM_CTX = 1024  # Small context window (faster on CPU)
LLM_NUM_THREAD = 4  # CPU threads for Raspberry Pi
LLM_TIMEOUT = 300  # 5 min timeout for slow CPU inference

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

# --- System Prompt (kept short for CPU performance) ---
SYSTEM_PROMPT = """You are Maya. Reply in ONE short sentence (max 10 words). Be warm and caring."""

# --- Ensure data directories exist ---
MEMORY_DIR.mkdir(parents=True, exist_ok=True)
