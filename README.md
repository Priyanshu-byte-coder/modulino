# Maya — Wellbeing AI Companion

A fully offline, privacy-first AI mental wellbeing companion designed to run on **Raspberry Pi 5**. Maya combines a local LLM, real-time facial emotion detection, text sentiment analysis, and long-term conversational memory to provide empathetic, context-aware support — all without any data ever leaving the device.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Hardware Requirements](#hardware-requirements)
- [Software Stack & Models](#software-stack--models)
- [Complete Workflow](#complete-workflow)
- [Installation on Raspberry Pi 5](#installation-on-raspberry-pi-5)
- [Installation on Windows (Development)](#installation-on-windows-development)
- [Running the Application](#running-the-application)
- [Configuration Reference](#configuration-reference)
- [Module Deep Dive](#module-deep-dive)
- [Web Interface](#web-interface)
- [Utility Scripts](#utility-scripts)
- [Troubleshooting](#troubleshooting)
- [Privacy & Security](#privacy--security)

---

## Overview

Maya is an AI-powered wellbeing companion that listens, understands, and responds with empathy. It runs **100% offline** on a Raspberry Pi 5, ensuring complete privacy. The system uses:

- A **local LLM** (Microsoft Phi-3 Mini via Ollama) for natural conversation
- **VADER sentiment analysis** to understand the emotional tone of text
- **FER (Facial Expression Recognition)** with a webcam for real-time facial emotion detection
- **ChromaDB** vector database for long-term conversational memory (RAG)
- An **Emotion Engine** that fuses text sentiment, facial emotion, and historical patterns into a unified mental state model

The companion is named **Maya** and provides brief, warm, supportive responses tailored to the user's current emotional state.

---

## Key Features

- **Fully Offline** — No internet required after initial setup. All inference happens locally on-device.
- **Privacy-First** — Zero data leaves the Raspberry Pi. No cloud APIs, no telemetry.
- **Multimodal Emotion Understanding** — Combines text sentiment + facial expression + conversation history.
- **Long-Term Memory (RAG)** — Remembers past conversations using ChromaDB vector similarity search and uses them to provide context-aware responses.
- **Dual Interface** — Terminal CLI for direct interaction, or a beautiful Flask web UI accessible from any device on the local network.
- **Real-Time Camera Feed** — Web interface shows live camera feed with emotion overlay and bounding boxes.
- **Streaming Responses** — LLM responses stream token-by-token via Server-Sent Events (SSE) for a responsive feel.
- **Modular Architecture** — Clean separation of concerns with abstract base classes for camera and display, making it easy to swap hardware (e.g., USB webcam vs RPi Camera Module, terminal vs E-Ink display).
- **RPi 5 Optimized** — Tuned context windows, thread counts, token limits, and sampling intervals for ARM64 CPU inference.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interfaces                         │
│  ┌──────────────────────┐    ┌───────────────────────────────┐  │
│  │   Terminal CLI        │    │   Flask Web App (port 5000)   │  │
│  │   (main.py)           │    │   (web_app.py + index.html)   │  │
│  └──────────┬───────────┘    └──────────────┬────────────────┘  │
└─────────────┼───────────────────────────────┼───────────────────┘
              │                               │
              ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                       AgentBrain (brain.py)                      │
│          Central orchestrator — coordinates all modules          │
│                                                                  │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────┐ ┌────────────┐ │
│  │ LLMClient   │ │ Sentiment    │ │ Emotion   │ │ Conversa-  │ │
│  │ (llm.py)    │ │ Analyzer     │ │ Engine    │ │ tion       │ │
│  │             │ │ (sentiment.  │ │ (emotion. │ │ Memory     │ │
│  │ Ollama API  │ │  py)         │ │  py)      │ │ (memory.py)│ │
│  │ phi3:mini   │ │ VADER        │ │ Fusion    │ │ ChromaDB   │ │
│  └─────────────┘ └──────────────┘ └───────────┘ └────────────┘ │
└─────────────────────────────────────────────────────────────────┘
              │                                        │
              ▼                                        ▼
┌──────────────────────┐               ┌──────────────────────────┐
│   Ollama Server      │               │  Camera Module           │
│   (localhost:11434)  │               │  (camera.py)             │
│   LLM Inference      │               │  OpenCV + FER            │
└──────────────────────┘               └──────────────────────────┘
```

---

## Project Structure

```
wellbeing_ai/
├── main.py                  # Terminal CLI entry point
├── web_app.py               # Flask web application entry point
├── requirements.txt         # Python dependencies
├── setup_rpi.sh             # Automated setup script for Raspberry Pi (Linux)
├── setup_rpi.bat            # Automated setup script for Windows development
├── patch_fer.py             # Patches FER library to fix moviepy import on RPi
├── reset_memory.py          # Utility to clear all stored conversations
├── view_memory.py           # Utility to view stored conversations
├── test_camera.py           # Camera & FER diagnostic test script
│
├── agent/                   # Core AI agent modules
│   ├── __init__.py
│   ├── brain.py             # AgentBrain — central orchestrator
│   ├── llm.py               # LLMClient — Ollama REST API integration
│   ├── sentiment.py         # SentimentAnalyzer — VADER-based text sentiment
│   ├── emotion.py           # EmotionEngine — multimodal emotion fusion
│   └── memory.py            # ConversationMemory — ChromaDB RAG store
│
├── config/                  # Configuration
│   ├── __init__.py
│   └── config.py            # All tuneable parameters (LLM, camera, paths, etc.)
│
├── interface/               # Hardware abstraction layers
│   ├── __init__.py
│   ├── camera.py            # BaseCamera / WebcamCamera — webcam + FER
│   └── display.py           # BaseDisplay / TerminalDisplay — output rendering
│
├── templates/               # Flask HTML templates
│   └── index.html           # Web chat interface (glassmorphism UI)
│
├── data/                    # Runtime data (auto-created)
│   └── memory/              # ChromaDB persistent storage
│
└── .gitignore               # Git ignore rules
```

---

## Hardware Requirements

### Target: Raspberry Pi 5

| Component | Specification |
|---|---|
| **Board** | Raspberry Pi 5 (4GB or 8GB RAM recommended) |
| **Storage** | 32GB+ microSD card (Class 10 / UHS-I minimum) |
| **Camera** | USB Webcam or Raspberry Pi Camera Module v2/v3 |
| **Power** | Official RPi 5 USB-C power supply (5V/5A) |
| **Network** | Required only for initial setup (downloading models & packages) |
| **Display** | Optional — web interface accessible from any device on LAN |

### Development: Any PC

- Windows, macOS, or Linux with Python 3.10+
- Webcam (for testing emotion detection)
- 8GB+ RAM recommended

---

## Software Stack & Models

### Language Model (LLM)

| Property | Value |
|---|---|
| **Model** | Microsoft Phi-3 Mini (`phi3:mini`) |
| **Runtime** | Ollama (local inference server) |
| **Parameters** | ~3.8B parameters |
| **Quantization** | Q4_K_M (default Ollama quantization) |
| **Context Window** | 1024 tokens (tuned for RPi CPU performance) |
| **Max Output Tokens** | 60 (brief, focused responses) |
| **Temperature** | 0.3 (low creativity, high consistency) |
| **CPU Threads** | 4 (matches RPi 5's quad-core Cortex-A76) |
| **Timeout** | 300 seconds (5 min for slow CPU inference) |
| **API** | Ollama REST API at `http://localhost:11434` |
| **Stop Sequences** | `\n\n`, `User:`, `Assistant:` |

**Why Phi-3 Mini?** — It is one of the smallest high-quality LLMs that can run on RPi 5 hardware with acceptable latency. It handles empathetic conversation well within tight token budgets.

### Sentiment Analysis

| Property | Value |
|---|---|
| **Library** | VADER (Valence Aware Dictionary and sEntiment Reasoner) |
| **Package** | `vaderSentiment>=3.3.2` |
| **Type** | Rule-based, lexicon-driven |
| **Output** | Compound score (-1.0 to +1.0), pos/neg/neu breakdown |
| **Thresholds** | Positive: ≥ 0.05, Negative: ≤ -0.05 |
| **Why VADER?** | Zero-latency, no GPU needed, specifically tuned for social/conversational text |

### Facial Emotion Recognition

| Property | Value |
|---|---|
| **Library** | FER (Facial Expression Recognition) v22.5.1 |
| **Backend** | TensorFlow (Keras CNN) |
| **Face Detector** | OpenCV Haar Cascade (`mtcnn=False` for speed on RPi) |
| **Detectable Emotions** | happy, sad, angry, fear, surprise, neutral, disgust |
| **Confidence Threshold** | 0.30 (detections below this are discarded) |
| **Sampling Interval** | Every 3 conversation turns (CLI) or every 2.5s (web UI polling) |
| **Why not MTCNN?** | MTCNN is more accurate but significantly slower on CPU. Haar Cascade provides adequate speed on RPi 5. |

### Vector Memory (RAG)

| Property | Value |
|---|---|
| **Database** | ChromaDB (persistent mode) |
| **Package** | `chromadb>=0.4.22` |
| **Embedding** | ChromaDB's default all-MiniLM-L6-v2 Sentence Transformer |
| **Distance Metric** | Cosine similarity (`hnsw:space: cosine`) |
| **Retrieval Top-K** | 2 (reduced for CPU performance) |
| **Storage Location** | `data/memory/` (auto-created) |
| **Collection Name** | `conversations` |
| **Stored Metadata** | user_message, assistant_response, sentiment_label, sentiment_score, emotion, timestamp |

### Web Framework

| Property | Value |
|---|---|
| **Framework** | Flask 3.0+ |
| **CORS** | flask-cors 4.0+ |
| **Streaming** | Server-Sent Events (SSE) via `/api/chat_stream` |
| **Host** | `0.0.0.0:5000` (accessible on LAN) |
| **Template** | Single-page glassmorphism UI (`templates/index.html`) |
| **Font** | Google Quicksand (loaded via CDN on first access) |

### Computer Vision

| Property | Value |
|---|---|
| **Library** | OpenCV (headless) `opencv-python-headless>=4.8.0` |
| **Usage** | Camera capture, color conversion (BGR→RGB), bounding box drawing, JPEG encoding |

### Other Dependencies

| Package | Version | Purpose |
|---|---|---|
| `requests` | ≥2.31.0 | HTTP client for Ollama REST API |
| `numpy` | ≥1.24.0, <2.0.0 | Array operations for OpenCV/TF (pinned <2.0 for compatibility) |
| `tensorflow` | ≥2.15.0, <2.18.0 | Backend for FER emotion detection CNN |

---

## Complete Workflow

### Per-Message Processing Pipeline

When a user sends a message, the `AgentBrain.process()` method orchestrates this pipeline:

```
User Input (text)
     │
     ▼
┌─────────────────────────────────┐
│ 1. SENTIMENT ANALYSIS           │
│    SentimentAnalyzer.analyze()  │
│    VADER scores the text →      │
│    label: positive/negative/    │
│           neutral               │
│    compound: -1.0 to +1.0      │
│    intensity: 0.0 to 1.0       │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 2. MEMORY RETRIEVAL (RAG)       │
│    ConversationMemory.retrieve()│
│    Query ChromaDB with user     │
│    input → retrieve top-2 most  │
│    semantically similar past    │
│    conversations                │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 3. EMOTION ENGINE UPDATE        │
│    EmotionEngine.update()       │
│    Fuses:                       │
│    • Text sentiment (VADER)     │
│    • Facial emotion (FER/cam)   │
│    • Historical sentiment avg   │
│    • Memory sentiment patterns  │
│    Outputs: MentalState object  │
│    (dominant_emotion, trend,    │
│     historical_avg)             │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 4. LLM RESPONSE GENERATION     │
│    LLMClient.chat()             │
│    Builds system prompt with:   │
│    • Base persona (Maya)        │
│    • Current user mood          │
│    • Emotional trend guidance   │
│    • Retrieved memory context   │
│    Sends last 4 messages +      │
│    system prompt to Ollama      │
│    Streams response tokens      │
└────────────┬────────────────────┘
             │
             ▼
┌─────────────────────────────────┐
│ 5. MEMORY STORAGE               │
│    ConversationMemory.store()   │
│    Stores in ChromaDB:          │
│    • user_message               │
│    • assistant_response         │
│    • sentiment_label & score    │
│    • dominant emotion           │
│    • timestamp                  │
│    Embedded for future RAG      │
└─────────────────────────────────┘
```

### Emotion Fusion Logic (`EmotionEngine`)

The Emotion Engine maintains a sliding window (10 turns) of sentiment scores and emotion labels to compute:

1. **Dominant Emotion Resolution** — If a facial emotion is detected (not `unknown`/`None`), it takes priority. Otherwise, text sentiment is mapped: positive→happy, negative→sad, neutral→neutral.
2. **Historical Sentiment Average** — Running mean of compound scores over the window.
3. **Emotional Trend** — Compares the average sentiment of the first half vs second half of the window. Difference >0.15 = "improving", <-0.15 = "declining", else "stable".
4. **Memory Pattern Adjustment** — If >60% of retrieved memories have negative sentiment, the historical average is shifted down by 0.1 to increase concern.

### Camera Emotion Flow (Web UI)

```
Browser polls /api/camera/snapshot every 2.5s
     │
     ▼
WebcamCamera.capture_snapshot_with_overlay()
     │
     ├── cv2.VideoCapture.read() → raw BGR frame
     ├── FER.detect_emotions(RGB frame) → bounding boxes + emotion scores
     ├── Draw green bounding box + emotion label on frame
     ├── cv2.imencode('.jpg') → JPEG bytes
     │
     ▼
Response: { image: base64 JPEG, emotion: "happy" }
     │
     ▼
Browser updates camera feed image + emotion emoji/label
```

---

## Installation on Raspberry Pi 5

### Prerequisites

- Raspberry Pi OS (64-bit / Bookworm recommended)
- Python 3.10 or higher
- Internet connection (for initial setup only)

### Automated Setup

```bash
# Clone the repository
git clone <repository-url> ~/wellbeing_ai
cd ~/wellbeing_ai

# Run the setup script
chmod +x setup_rpi.sh
./setup_rpi.sh
```

The script will:
1. Create a Python virtual environment
2. Install all pip dependencies
3. Create the `data/memory/` directory
4. Install Ollama (if not already installed)
5. Pull the `phi3:mini` model

### Manual Setup

```bash
# 1. Install system dependencies
sudo apt update && sudo apt install -y python3 python3-pip python3-venv libatlas-base-dev

# 2. Create & activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Patch FER for RPi (fixes moviepy import error)
python patch_fer.py

# 6. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# 7. Start Ollama and pull the model
ollama serve &
sleep 3
ollama pull phi3:mini

# 8. Create data directory
mkdir -p data/memory

# 9. Enable camera (if using RPi Camera Module)
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Reboot if prompted
```

---

## Installation on Windows (Development)

```batch
REM Clone the repository
git clone <repository-url>
cd wellbeing_ai

REM Run the setup script
setup_rpi.bat
```

Or manually:

```batch
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

REM Install Ollama from https://ollama.com/download/windows
ollama pull phi3:mini
```

---

## Running the Application

### Terminal CLI

```bash
source venv/bin/activate   # Linux/RPi
# OR
venv\Scripts\activate      # Windows

python main.py
```

This launches an interactive terminal session where you type messages and Maya responds. Camera emotion detection samples every 3 turns (configurable).

### Web Interface

```bash
source venv/bin/activate   # Linux/RPi

python web_app.py
```

Then open in a browser:
- **On the Pi**: `http://localhost:5000`
- **From another device on LAN**: `http://<raspberry-pi-ip>:5000`

The web interface provides:
- A chat window with streaming responses
- Live camera feed with emotion overlay (bounding boxes + labels)
- Real-time emotion emoji display
- System status indicators (LLM, Memory, Camera)
- Conversation reset button

---

## Configuration Reference

All configuration lives in `config/config.py`. Key settings:

| Setting | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL (env: `OLLAMA_BASE_URL`) |
| `LLM_MODEL` | `phi3:mini` | Ollama model name (env: `LLM_MODEL`) |
| `LLM_TEMPERATURE` | `0.3` | Creativity vs consistency (0.0–1.0) |
| `LLM_MAX_TOKENS` | `60` | Max response length in tokens |
| `LLM_NUM_CTX` | `1024` | Context window size |
| `LLM_NUM_THREAD` | `4` | CPU threads (matches RPi 5 quad-core) |
| `LLM_TIMEOUT` | `300` | Request timeout in seconds |
| `CAMERA_ENABLED` | `True` | Enable/disable camera subsystem |
| `CAMERA_INDEX` | `0` | OpenCV camera device index |
| `CAMERA_SAMPLE_INTERVAL` | `3` | Capture emotion every N turns (CLI) |
| `MEMORY_COLLECTION` | `conversations` | ChromaDB collection name |
| `MEMORY_TOP_K` | `2` | Number of memories to retrieve per query |
| `DISPLAY_MODE` | `terminal` | Display mode (`terminal` or `eink`) |
| `SYSTEM_PROMPT` | Maya persona | System prompt sent to the LLM |

### Environment Variables

These settings can be overridden via environment variables:
- `OLLAMA_BASE_URL`
- `LLM_MODEL`
- `CAMERA_ENABLED` (set to `"true"` / `"false"`)
- `DISPLAY_MODE`

---

## Module Deep Dive

### `agent/brain.py` — AgentBrain

The central orchestrator. Initializes all subsystems and exposes:
- `check_systems()` → dict of subsystem health checks
- `process(user_input, face_emotion, stream)` → runs the full 5-step pipeline (sentiment → memory retrieval → emotion update → LLM generation → memory storage)
- Maintains a rolling conversation history (last 4 messages sent to LLM)
- Builds a dynamic system prompt that includes Maya's persona, current user mood, emotional trend guidance, and retrieved memory context

### `agent/llm.py` — LLMClient

Communicates with Ollama's REST API:
- `is_available()` → checks if Ollama is running and the model is loaded (via `/api/tags`)
- `generate(prompt, system)` → single-shot generation via `/api/generate` (streaming internally)
- `chat(messages, stream_output)` → chat-style generation via `/api/chat`. When `stream_output=True`, returns a generator that yields tokens one by one for SSE streaming.
- Handles connection errors, timeouts, and server unavailability gracefully with error messages.

### `agent/sentiment.py` — SentimentAnalyzer

Wraps VADER for conversational sentiment analysis:
- `analyze(text)` → returns `SentimentResult(label, compound, intensity, scores)`
- Labels: `positive` (compound ≥ 0.05), `negative` (compound ≤ -0.05), `neutral`
- Intensity = absolute value of compound score (0.0–1.0)
- Zero dependencies beyond `vaderSentiment`, instant CPU execution

### `agent/emotion.py` — EmotionEngine

Maintains session-level emotional state:
- `update(sentiment, face_emotion, retrieved_memories)` → returns `MentalState`
- Tracks a sliding window of 10 sentiment scores and emotion labels
- Resolves dominant emotion (face > text mapping)
- Computes emotional trend (improving / declining / stable)
- Adjusts for long-term memory patterns (negative memory ratio)

### `agent/memory.py` — ConversationMemory

ChromaDB-backed long-term memory with RAG:
- `store(MemoryEntry)` → stores a conversation turn with full metadata
- `retrieve(query, top_k)` → semantic similarity search, returns `list[RetrievedMemory]`
- Uses cosine distance in HNSW index
- Each entry stores: user message, assistant response, sentiment label/score, emotion, timestamp
- Documents are formatted as `"User: ...\nAssistant: ..."` for embedding

### `interface/camera.py` — BaseCamera / WebcamCamera

Hardware abstraction for camera + emotion detection:
- `BaseCamera` — abstract base class defining the interface
- `WebcamCamera` — implementation using OpenCV + FER
- `capture_emotion()` → capture frame, detect dominant emotion, return label or None
- `capture_frame()` → return raw OpenCV frame
- `capture_snapshot_with_overlay()` → capture frame, detect emotion, draw bounding box + label, return (JPEG bytes, emotion label)
- `is_available()` → check if camera is accessible
- `release()` → release camera resources
- FER initialization is optional — if TensorFlow/FER is unavailable, the camera still works for frame capture without emotion detection

### `interface/display.py` — BaseDisplay / TerminalDisplay

Hardware abstraction for output rendering:
- `BaseDisplay` — abstract base class
- `TerminalDisplay` — rich terminal output with text wrapping
- `show_message(sender, message)` — formatted chat output
- `show_welcome()` — welcome banner
- `show_emotion(emotion)` — emoji-mapped emotion display
- `show_status(status)` — system status messages
- `clear()` — clear terminal screen (platform-aware: `cls` on Windows, `clear` on Linux)
- Designed to be replaceable with an E-Ink display implementation

### `web_app.py` — Flask Web Application

REST API + SSE streaming server:
- `GET /` — serves the chat interface (`templates/index.html`)
- `GET /api/status` — returns system health (LLM, memory, camera)
- `POST /api/chat` — synchronous chat endpoint (returns full response)
- `POST /api/chat_stream` — SSE streaming chat endpoint (yields tokens)
- `GET /api/camera/snapshot` — returns base64 JPEG with emotion overlay
- `GET /api/camera/emotion` — returns detected emotion label only
- `POST /api/reset` — resets conversation history

### `templates/index.html` — Web Chat Interface

Single-page application with:
- **Glassmorphism UI** — frosted glass panels with gradient background
- **Chat panel** — message bubbles with avatars, typing indicator, auto-scroll
- **Emotion sidebar** — live camera feed, emotion emoji display, status indicators
- **SSE streaming** — reads token-by-token from `/api/chat_stream` using `ReadableStream`
- **Emotion polling** — polls `/api/camera/snapshot` every 2.5 seconds for live emotion updates
- **Responsive** — adapts to mobile screens with stacked layout
- **Font** — Google Quicksand for a friendly, approachable feel

---

## Utility Scripts

### `test_camera.py`

Diagnostic script that tests the full camera pipeline in 4 steps:
1. Webcam access (OpenCV)
2. FER library import
3. FER detector initialization
4. Live emotion detection with confidence scores

```bash
python test_camera.py
```

### `patch_fer.py`

Patches the FER library's `classes.py` to make the `moviepy` import optional. This fixes the `"No module named 'moviepy.editor'"` error that occurs on Raspberry Pi since moviepy is not needed for emotion detection.

```bash
python patch_fer.py
```

### `reset_memory.py`

Deletes all stored conversations from ChromaDB. Asks for confirmation before proceeding.

```bash
python reset_memory.py
```

### `view_memory.py`

Displays all stored conversations with timestamps, sentiment labels, emotions, and message previews.

```bash
python view_memory.py
```

---

## Troubleshooting

### Ollama not running

```
[!] Ollama is not running or model not found.
```

**Fix:**
```bash
ollama serve &          # Start Ollama server
ollama pull phi3:mini   # Download the model
```

### Camera not detected

```
⚠️ Camera enabled but not available
```

**Fix (RPi Camera Module):**
```bash
sudo raspi-config       # Interface Options → Camera → Enable
sudo reboot
```

**Fix (USB Webcam):**
```bash
ls /dev/video*          # Check available camera devices
# If your camera is at /dev/video1, set CAMERA_INDEX=1 in config/config.py
```

### FER moviepy import error

```
No module named 'moviepy.editor'
```

**Fix:**
```bash
python patch_fer.py
```

### Slow LLM responses

This is expected on RPi 5 CPU. Responses may take 30–120 seconds. To improve:
- Reduce `LLM_MAX_TOKENS` in `config/config.py`
- Reduce `LLM_NUM_CTX` (smaller context = faster)
- Ensure no other heavy processes are running

### TensorFlow / NumPy compatibility

If you see numpy-related errors:
```bash
pip install "numpy>=1.24.0,<2.0.0"
pip install --force-reinstall "tensorflow>=2.15.0,<2.18.0"
```

### ChromaDB SQLite errors

On some RPi OS versions, the system SQLite may be too old:
```bash
pip install pysqlite3-binary
```

---

## Privacy & Security

- **All processing happens locally** on the Raspberry Pi. No data is sent to any external server.
- **Ollama runs locally** — the LLM never contacts the internet during inference.
- **ChromaDB stores data locally** in `data/memory/` on the device's filesystem.
- **Camera frames are processed in-memory** and never saved to disk (only emotion labels are stored).
- **The web interface binds to `0.0.0.0:5000`** — it is accessible on the local network. For additional security, configure a firewall to restrict access to trusted devices only.
- **No API keys** are required. No accounts, no cloud services, no telemetry.

---

## License

This project is intended for personal and educational use.
