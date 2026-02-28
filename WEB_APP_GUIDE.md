# Web Application Guide

## Overview
The Wellbeing AI Companion now has a browser-based interface that you can access on your Raspberry Pi or any device on the same network.

## Installation

1. **Install the new dependencies:**
   ```bash
   pip install flask flask-cors
   ```
   
   Or reinstall all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. **Make sure Ollama is running:**
   ```bash
   ollama serve
   ```

3. **Ensure the phi3:mini model is available:**
   ```bash
   ollama pull phi3:mini
   ```

## Running the Web Application

### On your laptop (for testing):
```bash
python web_app.py
```

### On Raspberry Pi:
```bash
python web_app.py
```

The application will start on port 5000 and be accessible at:
- **Local access:** http://localhost:5000
- **From other devices:** http://<raspberry-pi-ip>:5000

To find your Raspberry Pi's IP address:
```bash
hostname -I
```

## Features

### 💬 Chat Interface
- Modern, responsive chat UI with gradient design
- Real-time messaging with Maya, your AI companion
- Conversation history displayed in a clean message format

### 📷 Camera Integration
- Click the camera button (📷) to capture your facial emotion
- The AI will consider your detected emotion when responding
- Camera must be enabled in `config/config.py` (set `CAMERA_ENABLED=true`)

### 🔄 System Status
- Real-time status indicators for:
  - **LLM**: Ollama connection status
  - **Memory**: ChromaDB/RAG system
  - **Camera**: Webcam/Pi Camera availability
- Green dot = active, Red dot = inactive

### 🗑️ Reset Conversation
- Click "Reset Chat" to start a fresh conversation
- Clears conversation history but preserves long-term memory

## Configuration

Edit `config/config.py` to customize:

```python
# Enable camera for emotion detection
CAMERA_ENABLED = True  # Set to False to disable

# Change the LLM model
LLM_MODEL = "phi3:mini"  # Or any other Ollama model

# Adjust response length
LLM_MAX_TOKENS = 500  # Increase for longer responses
```

## API Endpoints

The web app exposes several REST API endpoints:

- `GET /` - Main chat interface
- `GET /api/status` - System status check
- `POST /api/chat` - Send a message and get response
- `GET /api/camera/snapshot` - Capture camera frame
- `GET /api/camera/emotion` - Detect emotion from camera
- `POST /api/reset` - Reset conversation history

## Troubleshooting

### "Ollama is not running"
Make sure Ollama is started:
```bash
ollama serve
```

### Camera not working
1. Check if camera is enabled in config
2. Verify camera permissions
3. On Raspberry Pi, ensure camera module is enabled:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > Camera > Enable
   ```

### Cannot access from other devices
1. Check firewall settings
2. Ensure the Raspberry Pi and your device are on the same network
3. Use the correct IP address (not localhost)

## Running on Startup (Raspberry Pi)

To run the web app automatically on boot:

1. Create a systemd service file:
   ```bash
   sudo nano /etc/systemd/system/wellbeing-ai.service
   ```

2. Add the following content:
   ```ini
   [Unit]
   Description=Wellbeing AI Web Application
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/wellbeing_ai
   ExecStart=/home/pi/wellbeing_ai/venv/bin/python web_app.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. Enable and start the service:
   ```bash
   sudo systemctl enable wellbeing-ai
   sudo systemctl start wellbeing-ai
   ```

4. Check status:
   ```bash
   sudo systemctl status wellbeing-ai
   ```

## Security Note

The web app runs on `0.0.0.0:5000`, making it accessible from any device on your network. For production use:
- Consider adding authentication
- Use HTTPS with SSL certificates
- Restrict access to specific IP addresses
- Run behind a reverse proxy (nginx/apache)

## Comparison: Terminal vs Web Interface

| Feature | Terminal (`main.py`) | Web App (`web_app.py`) |
|---------|---------------------|------------------------|
| Interface | Command-line | Browser-based |
| Access | Local only | Network-accessible |
| Camera | Auto-sampling | On-demand button |
| Multi-device | No | Yes |
| Mobile-friendly | No | Yes |
| Visual design | Basic | Modern UI |

Both interfaces use the same AI brain and memory system!
