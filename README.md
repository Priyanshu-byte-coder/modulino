# 🤗 Wellbeing AI Companion

A fully offline, privacy-preserving mental well-being support assistant with multimodal emotional intelligence.

**Designed for laptop development with seamless migration to Raspberry Pi (16GB RAM) + E-Ink display + camera.**

## ✨ Features

- 🧠 **Local LLM** — Phi-3 Mini via Ollama (fully offline)
- 💭 **Sentiment Analysis** — VADER-based real-time emotion detection from text
- 📷 **Facial Emotion Detection** — FER library with 7 emotions (happy, sad, angry, fear, surprise, neutral, disgust)
- 🧬 **Emotional Intelligence** — Fuses text sentiment + facial emotion + historical trends
- 💾 **Long-term Memory** — ChromaDB with RAG for conversational continuity
- 🔒 **100% Offline** — No cloud APIs, no data leaves your device
- 🎨 **Hardware Abstraction** — Easy migration to E-Ink displays and Pi Camera
- 🌐 **Web Interface** — Modern browser-based UI accessible on any device
- 📱 **Mobile-Friendly** — Responsive design works on phones, tablets, and desktops

## Architecture

```
wellbeing_ai/
├── agent/
│   ├── brain.py        # Central orchestrator
│   ├── llm.py          # Ollama LLM client
│   ├── sentiment.py    # VADER sentiment analysis
│   ├── emotion.py      # Emotional intelligence layer
│   └── memory.py       # ChromaDB RAG memory
├── interface/
│   ├── display.py      # Terminal UI (→ E-Ink later)
│   └── camera.py       # Webcam stub (→ Pi Camera later)
├── config/
│   └── config.py       # All settings in one place
├── templates/
│   └── index.html      # Web interface UI
├── data/
│   └── memory/         # Persistent ChromaDB storage
├── main.py             # Terminal entry point
├── web_app.py          # Web interface entry point
├── setup_rpi.sh        # Automated setup for Linux/Pi
├── setup_rpi.bat       # Automated setup for Windows
├── requirements.txt
└── README.md
```

## 📋 Prerequisites

### Software
- **Python 3.10+** (3.11 recommended)
- **Ollama** — Local LLM inference server
- **Git** (for cloning)

### Hardware (Minimum)
- **Laptop/Desktop**: 8GB RAM, 10GB free disk space
- **Raspberry Pi**: Pi 4/5 with 16GB RAM (8GB minimum)

### Optional Hardware
- Webcam or Raspberry Pi Camera Module (for emotion detection)
- E-Ink display (Waveshare 7.5" or similar, for final deployment)

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**On Raspberry Pi / Linux:**
```bash
git clone https://github.com/Priyanshu-byte-coder/modulino.git
cd modulino
chmod +x setup_rpi.sh
./setup_rpi.sh
```

**On Windows:**
```bash
git clone https://github.com/Priyanshu-byte-coder/modulino.git
cd modulino
setup_rpi.bat
```

### Option 2: Manual Setup

#### 1. Install Ollama

Download from [https://ollama.com](https://ollama.com) and install.

```bash
# Start the server
ollama serve

# Pull a small quantized model (in a separate terminal)
ollama pull phi3:mini
```

#### 2. Create virtual environment and install dependencies

```bash
cd wellbeing_ai
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

#### 3. Run the assistant

**Terminal Interface:**
```bash
python main.py
```

**Web Interface (Browser-based):**
```bash
python web_app.py
# Open browser to: http://localhost:5000
```

## ⚙️ Configuration

All settings are in `config/config.py`. Key configuration options:

| Variable | Default | Description |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `LLM_MODEL` | `phi3:mini` | LLM model name |
| `CAMERA_ENABLED` | `false` | Enable webcam emotion detection |
| `CAMERA_SAMPLE_INTERVAL` | `3` | Capture emotion every N turns |
| `DISPLAY_MODE` | `terminal` | Display type: `terminal` or `eink` |
| `MEMORY_DIR` | `data/memory` | ChromaDB storage location |
| `MEMORY_COLLECTION` | `conversations` | ChromaDB collection name |

### Enable Camera Emotion Detection

```powershell
# Windows
$env:CAMERA_ENABLED="true"
python main.py

# Or edit config/config.py directly
CAMERA_ENABLED = True
```

## 🧩 System Architecture

### Core Modules

#### 1. **LLM Client** (`agent/llm.py`)
- Ollama REST API client
- Supports any GGUF model (Phi-3, Llama, Mistral, etc.)
- Streaming and non-streaming responses
- Automatic retry logic

#### 2. **Sentiment Analyzer** (`agent/sentiment.py`)
- VADER (Valence Aware Dictionary and sEntiment Reasoner)
- Zero-GPU, instant analysis
- Compound score: -1.0 (very negative) to +1.0 (very positive)
- Intensity scoring for emotional strength

#### 3. **Memory System** (`agent/memory.py`)
- ChromaDB vector database
- Semantic search with embeddings
- RAG (Retrieval-Augmented Generation)
- Stores: user message, assistant response, sentiment, emotion, timestamp
- Retrieves top 5 most relevant past conversations

#### 4. **Emotion Engine** (`agent/emotion.py`)
- Fuses multiple emotion signals:
  - Text sentiment (VADER)
  - Facial emotion (FER)
  - Historical emotional trend
- Outputs unified mental state model
- Tracks emotional trajectory (stable/improving/declining)

#### 5. **Agent Brain** (`agent/brain.py`)
- Central orchestrator
- Pipeline: Sentiment → Memory Retrieval → Emotion Fusion → LLM → Storage
- Builds context-aware system prompts
- Manages conversation history

#### 6. **Camera Interface** (`interface/camera.py`)
- Abstract `BaseCamera` class
- `WebcamCamera`: OpenCV + FER for facial emotion detection
- 7 emotions: happy, sad, angry, fear, surprise, neutral, disgust
- Confidence thresholding (default: 0.3)
- Sampling control to optimize performance
- Future: `PiCamera` class for Raspberry Pi Camera Module

#### 7. **Display Interface** (`interface/display.py`)
- Abstract `BaseDisplay` class
- `TerminalDisplay`: Rich terminal UI with text wrapping
- Emotion emoji feedback (😊 😢 😠 😨 😮 😐 🤢)
- Future: `EInkDisplay` class for E-Ink displays

### Data Flow

```
User Input
    ↓
[Sentiment Analysis] ← VADER
    ↓
[Memory Retrieval] ← ChromaDB (semantic search)
    ↓
[Emotion Fusion] ← Text sentiment + Camera emotion + History
    ↓
[System Prompt] ← Mental state + Retrieved memories
    ↓
[LLM Generation] ← Ollama (Phi-3 Mini)
    ↓
[Memory Storage] ← Store conversation with metadata
    ↓
Assistant Response
```

## 🤖 Models and Dependencies

### LLM Models (via Ollama)

**Recommended for Laptop:**
- `phi3:mini` (3.8B params, ~2.3GB) — Best balance of speed and quality
- `phi3:medium` (14B params, ~7.9GB) — Higher quality, slower
- `llama3.2:3b` (3B params, ~2GB) — Fast alternative

**Recommended for Raspberry Pi:**
- `phi3:mini` (3.8B params, ~2.3GB) — Works well on 16GB Pi
- `tinyllama` (1.1B params, ~637MB) — Faster but less capable

**To change model:**
```bash
# Pull new model
ollama pull llama3.2:3b

# Update config/config.py
LLM_MODEL = "llama3.2:3b"
```

### Python Dependencies

**Core:**
- `requests>=2.31.0` — HTTP client for Ollama API
- `chromadb>=0.4.0` — Vector database for memory
- `vaderSentiment>=3.3.2` — Sentiment analysis

**Computer Vision:**
- `opencv-python>=4.8.0` — Webcam capture
- `fer==22.5.1` — Facial emotion recognition (pinned version)
- `tensorflow>=2.13.0` — Deep learning backend for FER
- `numpy>=1.26.0,<2.0.0` — Numerical computing

**Utilities:**
- `setuptools==69.5.1` — Required for FER compatibility

### Model Sizes

| Component | Size | Purpose |
|-----------|------|----------|
| Phi-3 Mini | ~2.3GB | LLM inference |
| FER Model | ~100MB | Facial emotion detection |
| ChromaDB | ~50MB + data | Vector database |
| Total (minimum) | ~2.5GB | Base installation |

## 🌐 Web Interface

The project includes a modern browser-based interface accessible from any device on your network.

### Features
- **Beautiful UI** — Modern gradient design with responsive layout
- **Real-time Chat** — Interactive messaging with Maya
- **Camera Integration** — On-demand emotion detection via camera button
- **System Status** — Live indicators for LLM, Memory, and Camera
- **Mobile-Friendly** — Works on phones, tablets, and desktops
- **Network Access** — Access from any device on the same network

### Running the Web App

```bash
python web_app.py
```

Access at:
- **Local:** http://localhost:5000
- **Network:** http://<device-ip>:5000

### Web Interface vs Terminal

| Feature | Terminal | Web Interface |
|---------|----------|---------------|
| Access | Local only | Network-wide |
| UI | Text-based | Modern browser UI |
| Camera | Auto-sampling | On-demand button |
| Mobile | No | Yes |
| Multi-user | No | Yes (shared session) |

**See detailed guide:** [`WEB_APP_GUIDE.md`](WEB_APP_GUIDE.md)

## 🛠️ Utility Scripts

### View Memory Database

```bash
python view_memory.py
```

Displays all stored conversations with:
- Timestamp
- User message and AI response
- Sentiment and emotion labels
- Total conversation count

### Reset Memory Database

```bash
python reset_memory.py
```

Clears all stored conversations:
- Asks for confirmation
- Shows count before deletion
- Creates fresh empty database
- Safe to run anytime

### Test Camera

```bash
python test_camera.py
```

Diagnostic script that tests:
1. Webcam access
2. FER library import
3. Detector initialization
4. Live emotion detection

## 📊 Performance Metrics

### Laptop (16GB RAM, i7 CPU)
- **Response time**: 2-5 seconds
- **Memory usage**: ~3GB
- **Camera capture**: ~1-2 seconds
- **Sentiment analysis**: <100ms

### Raspberry Pi 4 (16GB RAM)
- **Response time**: 5-15 seconds
- **Memory usage**: ~4GB
- **Camera capture**: ~2-3 seconds
- **Sentiment analysis**: <200ms

## 🔐 Privacy and Security

- ✅ **100% Offline** — No internet required after setup
- ✅ **Local Processing** — All AI runs on your device
- ✅ **No Telemetry** — No data sent to external servers
- ✅ **Local Storage** — All conversations stored locally in ChromaDB
- ✅ **No Cloud APIs** — No OpenAI, Anthropic, or other cloud services
- ✅ **Camera Privacy** — Frames processed locally, not stored

## 📱 Raspberry Pi Deployment

**See detailed guide:** [`RASPBERRY_PI_SETUP.md`](RASPBERRY_PI_SETUP.md)

Only two files need changes for full deployment:
1. `interface/display.py` — Add `EInkDisplay` class
2. `interface/camera.py` — Add `PiCamera` class

Agent logic (`agent/`) remains completely untouched.

### Quick Transfer

```bash
# From your laptop
scp -r wellbeing_ai pi@raspberrypi.local:~/

# On Raspberry Pi
cd ~/wellbeing_ai
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 🧪 Testing

### Phase 1: Core System (✅ Complete)
- LLM conversation
- Sentiment analysis
- Memory storage and retrieval
- Terminal display

### Phase 2: Camera Emotion Detection (✅ Complete)
- Webcam capture
- FER emotion detection
- Multimodal emotion fusion
- Visual feedback

### Phase 3: Raspberry Pi Deployment (⬜ Pending)
- E-Ink display integration
- Pi Camera integration
- Auto-start service
- Standalone operation

## 🐛 Troubleshooting

### FER Import Error

```bash
# Uninstall and reinstall with correct versions
pip uninstall fer tensorflow -y
pip install fer==22.5.1 tensorflow>=2.13.0 setuptools==69.5.1
```

### Ollama Connection Error

```bash
# Check if Ollama is running
ollama list

# Start Ollama server
ollama serve

# Test model
ollama run phi3:mini "Hello"
```

### Camera Not Detected

```bash
# Test camera access
python test_camera.py

# Check camera permissions (Linux/macOS)
ls -l /dev/video0

# Add user to video group (Linux)
sudo usermod -a -G video $USER
```

### Memory/ChromaDB Issues

```bash
# Reset database
python reset_memory.py

# View current state
python view_memory.py
```

## 📚 Project Structure

```
wellbeing_ai/
├── agent/                      # AI agent modules
│   ├── brain.py               # Central orchestrator
│   ├── llm.py                 # Ollama LLM client
│   ├── sentiment.py           # VADER sentiment analysis
│   ├── emotion.py             # Emotional intelligence layer
│   └── memory.py              # ChromaDB RAG memory
├── interface/                  # Hardware abstraction
│   ├── display.py             # Display interface (Terminal/E-Ink)
│   └── camera.py              # Camera interface (Webcam/PiCamera)
├── config/                     # Configuration
│   └── config.py              # All settings
├── data/                       # Persistent data
│   └── memory/                # ChromaDB storage
├── main.py                     # Entry point
├── test_camera.py             # Camera diagnostic tool
├── view_memory.py             # Memory viewer utility
├── reset_memory.py            # Memory reset utility
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── RASPBERRY_PI_SETUP.md      # Pi deployment guide
└── PHASE2_TESTING.md          # Camera testing guide
```

## 🤝 Contributing

This is a personal well-being assistant. Feel free to fork and customize for your own use.

## 📄 License

MIT License — Use freely for personal projects.

## 🙏 Acknowledgments

- **Ollama** — Local LLM inference
- **Microsoft Phi-3** — Efficient small language model
- **ChromaDB** — Vector database
- **VADER** — Sentiment analysis
- **FER** — Facial emotion recognition
- **OpenCV** — Computer vision

---

**Built with privacy and emotional intelligence in mind.** 🧠💙
