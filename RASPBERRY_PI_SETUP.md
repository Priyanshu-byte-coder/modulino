# Raspberry Pi Deployment Guide

Complete step-by-step instructions for deploying the Wellbeing AI Companion to Raspberry Pi 4/5 (16GB RAM recommended).

---

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Raspberry Pi OS Setup](#raspberry-pi-os-setup)
3. [Install System Dependencies](#install-system-dependencies)
4. [Install Ollama on Raspberry Pi](#install-ollama-on-raspberry-pi)
5. [Transfer Project Files](#transfer-project-files)
6. [Setup Python Environment](#setup-python-environment)
7. [Configure for Raspberry Pi](#configure-for-raspberry-pi)
8. [Test the Installation](#test-the-installation)
9. [Optional: E-Ink Display Setup](#optional-e-ink-display-setup)
10. [Optional: Pi Camera Setup](#optional-pi-camera-setup)
11. [Auto-Start on Boot](#auto-start-on-boot)
12. [Troubleshooting](#troubleshooting)

---

## Hardware Requirements

### Minimum Specifications
- **Raspberry Pi 4 or 5** (8GB RAM minimum, **16GB recommended**)
- **64GB+ microSD card** (Class 10 or better)
- **Power supply** (official 5V 3A USB-C recommended)
- **Internet connection** (for initial setup only)

### Optional Hardware
- **Webcam** or **Raspberry Pi Camera Module v2/v3** (for emotion detection)
- **E-Ink Display** (Waveshare 7.5" or similar, for final deployment)
- **Cooling fan/heatsink** (recommended for sustained LLM inference)

---

## Raspberry Pi OS Setup

### 1. Flash Raspberry Pi OS (64-bit)

**On your laptop:**

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/)
2. Insert microSD card
3. Flash **Raspberry Pi OS (64-bit)** — use "Raspberry Pi OS Lite (64-bit)" for headless setup
4. **Important**: Click settings (gear icon) and configure:
   - Set hostname: `wellbeing-pi`
   - Enable SSH
   - Set username: `pi` and password
   - Configure WiFi (SSID and password)
   - Set locale/timezone

5. Write to SD card and boot the Pi

### 2. First Boot and SSH Access

```bash
# Find your Pi's IP address (from your router or use)
ping wellbeing-pi.local

# SSH into the Pi
ssh pi@wellbeing-pi.local
# Or: ssh pi@<IP_ADDRESS>
```

### 3. Update System

```bash
sudo apt update
sudo apt upgrade -y
sudo reboot
```

---

## Install System Dependencies

SSH back into the Pi after reboot:

```bash
ssh pi@wellbeing-pi.local
```

### Install Required Packages

```bash
# Python and build tools
sudo apt install -y python3-pip python3-venv python3-dev

# OpenCV dependencies
sudo apt install -y libopencv-dev python3-opencv
sudo apt install -y libatlas-base-dev libhdf5-dev libhdf5-serial-dev
sudo apt install -y libjasper-dev libqtgui4 libqt4-test

# Camera support (if using camera)
sudo apt install -y libcamera-dev libcamera-apps

# Additional libraries
sudo apt install -y libssl-dev libffi-dev
sudo apt install -y git curl wget

# Optional: for E-Ink display
sudo apt install -y python3-pil python3-numpy
```

---

## Install Ollama on Raspberry Pi

### 1. Download and Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
```

### 2. Start Ollama Service

```bash
# Start Ollama server
ollama serve &

# Or enable as a system service
sudo systemctl enable ollama
sudo systemctl start ollama
```

### 3. Pull the LLM Model

**Important**: Use a small quantized model for Raspberry Pi.

```bash
# Recommended: Phi-3 Mini (3.8B parameters, ~2.3GB)
ollama pull phi3:mini

# Alternative lightweight models:
# ollama pull tinyllama        # 1.1B params, ~637MB (faster but less capable)
# ollama pull phi3:3.8b         # Full precision (larger)
```

**Note**: First pull will take 10-30 minutes depending on internet speed.

### 4. Test Ollama

```bash
# Test the model
ollama run phi3:mini "Hello, how are you?"

# If it responds, Ollama is working correctly!
```

---

## Transfer Project Files

### Method 1: Using SCP (from your laptop)

**On your laptop** (in the project directory):

```powershell
# Windows PowerShell
scp -r C:\Users\Priyanshu\OneDrive\Desktop\wellbeing_ai pi@wellbeing-pi.local:~/

# This transfers the entire project folder to /home/pi/wellbeing_ai
```

**macOS/Linux:**

```bash
scp -r ~/path/to/wellbeing_ai pi@wellbeing-pi.local:~/
```

### Method 2: Using Git (if you have a repository)

**On the Raspberry Pi:**

```bash
cd ~
git clone <your-repo-url> wellbeing_ai
cd wellbeing_ai
```

### Method 3: Using USB Drive

1. Copy `wellbeing_ai` folder to USB drive on laptop
2. Insert USB into Raspberry Pi
3. Mount and copy:

```bash
# Find USB device
lsblk

# Mount (assuming /dev/sda1)
sudo mount /dev/sda1 /mnt

# Copy files
cp -r /mnt/wellbeing_ai ~/
sudo umount /mnt
```

---

## Setup Python Environment

**On the Raspberry Pi:**

```bash
cd ~/wellbeing_ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

**Note**: Installation may take 30-60 minutes on Raspberry Pi due to compiling TensorFlow and other packages.

### If TensorFlow Installation Fails

TensorFlow can be tricky on ARM. Use the official wheel:

```bash
# For Raspberry Pi OS (64-bit)
pip install tensorflow-aarch64

# Or use TensorFlow Lite (lighter alternative)
pip install tflite-runtime
```

---

## Configure for Raspberry Pi

### 1. Verify Configuration

Check `config/config.py` — no changes needed if using defaults:

```python
# These should work out of the box on Pi
OLLAMA_BASE_URL = "http://localhost:11434"
LLM_MODEL = "phi3:mini"
CAMERA_ENABLED = False  # Enable after testing
DISPLAY_MODE = "terminal"  # Change to "eink" when ready
```

### 2. Test Without Camera First

```bash
cd ~/wellbeing_ai
source venv/bin/activate
python main.py
```

You should see:

```
================================================================================
                            🤗  Wellbeing AI Companion
               Your private, offline emotional support assistant
================================================================================
```

Type "hello" to test. If it responds, **core system is working!**

---

## Test the Installation

### 1. Test Core System

```bash
source venv/bin/activate
python main.py
```

**Test conversation:**
- Type: "hello"
- Type: "my name is [your name]"
- Type: "quit"
- Restart and type: "do you remember my name?"

If memory works, you're good!

### 2. Test Camera (if using webcam/Pi Camera)

```bash
# Enable camera
export CAMERA_ENABLED=true

# Test camera script
python test_camera.py
```

If camera test passes, run main app:

```bash
python main.py
```

### 3. View Stored Memory

```bash
python view_memory.py
```

### 4. Reset Memory (if needed)

```bash
python reset_memory.py
```

---

## Optional: E-Ink Display Setup

### For Waveshare E-Ink Displays

1. **Enable SPI Interface**

```bash
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
sudo reboot
```

2. **Install Waveshare Library**

```bash
cd ~
git clone https://github.com/waveshare/e-Paper.git
cd e-Paper/RaspberryPi_JetsonNano/python
pip install .
```

3. **Update Configuration**

Edit `config/config.py`:

```python
DISPLAY_MODE = "eink"
```

4. **Implement E-Ink Display Class**

You'll need to add the `EInkDisplay` class to `interface/display.py`. See the existing `TerminalDisplay` class as a template.

---

## Optional: Pi Camera Setup

### For Raspberry Pi Camera Module

1. **Enable Camera Interface**

```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
sudo reboot
```

2. **Test Camera**

```bash
# Test with libcamera
libcamera-hello --timeout 5000

# Or take a test photo
libcamera-jpeg -o test.jpg
```

3. **Update Camera Code**

Modify `interface/camera.py` to use `picamera2` instead of OpenCV:

```bash
pip install picamera2
```

The existing `WebcamCamera` class uses OpenCV, which works with USB webcams. For Pi Camera Module, you'll need to create a `PiCamera` class.

---

## Auto-Start on Boot

### Method 1: Systemd Service (Recommended)

Create a service file:

```bash
sudo nano /etc/systemd/system/wellbeing-ai.service
```

Add the following:

```ini
[Unit]
Description=Wellbeing AI Companion
After=network.target ollama.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/wellbeing_ai
Environment="PATH=/home/pi/wellbeing_ai/venv/bin"
Environment="CAMERA_ENABLED=true"
ExecStart=/home/pi/wellbeing_ai/venv/bin/python /home/pi/wellbeing_ai/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable wellbeing-ai.service
sudo systemctl start wellbeing-ai.service

# Check status
sudo systemctl status wellbeing-ai.service

# View logs
sudo journalctl -u wellbeing-ai.service -f
```

### Method 2: Cron Job

```bash
crontab -e
```

Add:

```bash
@reboot sleep 30 && cd /home/pi/wellbeing_ai && /home/pi/wellbeing_ai/venv/bin/python main.py
```

---

## Troubleshooting

### Issue: Ollama Not Found

```bash
# Check if Ollama is running
ps aux | grep ollama

# Start manually
ollama serve &

# Check if model is downloaded
ollama list
```

### Issue: Out of Memory

```bash
# Check memory usage
free -h

# Increase swap space
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Change CONF_SWAPSIZE=2048 (2GB)
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### Issue: TensorFlow Import Error

```bash
# Try TensorFlow Lite instead
pip uninstall tensorflow
pip install tflite-runtime
```

Then modify `interface/camera.py` to use TFLite models.

### Issue: Camera Not Working

```bash
# Check camera detection
ls /dev/video*

# For Pi Camera Module
libcamera-hello

# Check permissions
sudo usermod -a -G video pi
```

### Issue: Slow Response Times

- Use smaller model: `ollama pull tinyllama`
- Reduce context window in `config/config.py`
- Add cooling (fan/heatsink)
- Close other applications

### Issue: ChromaDB Errors

```bash
# Clear and rebuild memory
python reset_memory.py
```

---

## Performance Optimization

### 1. Overclock (Optional, at your own risk)

Edit `/boot/config.txt`:

```bash
sudo nano /boot/config.txt
```

Add (for Pi 4):

```ini
over_voltage=6
arm_freq=2000
gpu_freq=750
```

Reboot and monitor temperature:

```bash
vcgencmd measure_temp
```

### 2. Disable Unnecessary Services

```bash
sudo systemctl disable bluetooth
sudo systemctl disable avahi-daemon
```

### 3. Use Lighter Model

```bash
ollama pull tinyllama
```

Update `config/config.py`:

```python
LLM_MODEL = "tinyllama"
```

---

## Network Configuration

### Access from Other Devices

If you want to access the AI from other devices on your network:

1. **Find Pi's IP address:**

```bash
hostname -I
```

2. **Update Ollama to listen on all interfaces:**

```bash
# Edit Ollama service
sudo systemctl edit ollama.service
```

Add:

```ini
[Service]
Environment="OLLAMA_HOST=0.0.0.0:11434"
```

Restart:

```bash
sudo systemctl restart ollama
```

3. **Access from laptop:**

Update `config/config.py` on your laptop:

```python
OLLAMA_BASE_URL = "http://<PI_IP_ADDRESS>:11434"
```

---

## Backup and Restore

### Backup Memory Database

```bash
# On Raspberry Pi
cd ~/wellbeing_ai
tar -czf memory_backup_$(date +%Y%m%d).tar.gz data/memory/

# Copy to laptop
scp pi@wellbeing-pi.local:~/wellbeing_ai/memory_backup_*.tar.gz ~/
```

### Restore Memory

```bash
# On Raspberry Pi
cd ~/wellbeing_ai
tar -xzf memory_backup_YYYYMMDD.tar.gz
```

---

## Security Recommendations

1. **Change default password:**

```bash
passwd
```

2. **Setup SSH keys** (disable password auth):

```bash
# On laptop, generate key
ssh-keygen -t ed25519

# Copy to Pi
ssh-copy-id pi@wellbeing-pi.local

# Disable password auth
sudo nano /etc/ssh/sshd_config
# Set: PasswordAuthentication no
sudo systemctl restart ssh
```

3. **Setup firewall:**

```bash
sudo apt install ufw
sudo ufw allow ssh
sudo ufw enable
```

4. **Keep system updated:**

```bash
sudo apt update && sudo apt upgrade -y
```

---

## Next Steps

1. ✅ Test core system (LLM + memory)
2. ✅ Test camera emotion detection
3. ⬜ Implement E-Ink display class
4. ⬜ Implement Pi Camera class
5. ⬜ Setup auto-start service
6. ⬜ Build enclosure with display and camera
7. ⬜ Deploy as standalone device

---

## Support and Resources

- **Ollama Documentation**: https://ollama.com/docs
- **Raspberry Pi Documentation**: https://www.raspberrypi.com/documentation/
- **ChromaDB Documentation**: https://docs.trychroma.com/
- **Waveshare E-Ink**: https://www.waveshare.com/wiki/Main_Page

---

## Estimated Timeline

- **Initial Setup**: 2-3 hours
- **Software Installation**: 1-2 hours
- **Testing and Configuration**: 1 hour
- **E-Ink Display Integration**: 2-4 hours
- **Pi Camera Integration**: 1-2 hours
- **Total**: ~8-12 hours for complete deployment

---

**You now have a fully offline, privacy-preserving AI companion running on Raspberry Pi!** 🎉
