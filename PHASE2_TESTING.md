# Phase 2 — Camera Emotion Detection Testing Guide

## What's New in Phase 2

- **Real-time facial emotion detection** using FER (Facial Expression Recognition)
- **Webcam integration** with automatic face detection
- **Emotion-aware responses** — LLM adapts based on detected facial emotions
- **Smart sampling** — Camera captures every N turns (configurable) to reduce latency
- **Visual feedback** — Emoji indicators show detected emotions

## Detected Emotions

The FER model detects 7 emotions:
- **happy** 😊
- **sad** 😢
- **angry** 😠
- **fear** 😨
- **surprise** 😲
- **neutral** 😐
- **disgust** 🤢

## Installation

### 1. Install new dependencies

```powershell
pip install fer tensorflow
```

**Note**: TensorFlow is ~500MB. For Raspberry Pi, use `tensorflow-lite` instead (lighter weight).

### 2. Enable camera in config

Set environment variable:

```powershell
$env:CAMERA_ENABLED="true"
python main.py
```

Or edit `config/config.py` directly:
```python
CAMERA_ENABLED = True
```

## Testing Steps

### Test 1: Camera Availability Check

Run the app and verify camera status:

```powershell
python main.py
```

Expected output:
```
... llm: ✓
... sentiment: ✓
... memory: ✓
... camera: ✓
📷 Camera emotion detection active (sampling every 3 turns)
```

### Test 2: Emotion Detection

1. Start a conversation
2. On turn 3, 6, 9, etc., the camera will capture your face
3. You should see:
   ```
   ... Capturing emotion from camera...
   📷 Detected: happy 😊
   ```

### Test 3: Emotion-Aware Responses

Try expressing different emotions:

**Scenario A — Sad expression**
- Make a sad face on turn 3
- Type: "I'm feeling overwhelmed today"
- The LLM should respond with extra empathy (it sees both text sentiment + facial emotion)

**Scenario B — Happy expression**
- Smile on turn 6
- Type: "Things are going better now"
- The LLM should reflect your positive state

### Test 4: No Face Detected

- Turn away from camera on a sampling turn
- Expected: No emotion detected, system continues normally
- Log: "No face detected in frame."

## Configuration Options

### Sampling Interval

Edit `config/config.py`:

```python
CAMERA_SAMPLE_INTERVAL = 3  # Capture every 3 turns (default)
```

- **Lower value (1-2)**: More frequent emotion detection, higher latency
- **Higher value (5-10)**: Less frequent, better performance on Pi

### Confidence Threshold

Edit `interface/camera.py` line 89:

```python
if confidence < 0.3:  # Adjust threshold (0.0 to 1.0)
```

- **Lower (0.2)**: More detections, less accurate
- **Higher (0.5)**: Fewer detections, more confident

## Troubleshooting

### Camera not detected

```
camera: ✗
```

**Solutions**:
1. Check webcam permissions (Windows Settings → Privacy → Camera)
2. Close other apps using the camera (Zoom, Teams, etc.)
3. Try different camera index in `config.py`: `CAMERA_INDEX = 1`

### FER import error

```
ImportError: No module named 'fer'
```

**Solution**:
```powershell
pip install fer tensorflow
```

### Low FPS / Slow responses

**Solutions**:
1. Increase `CAMERA_SAMPLE_INTERVAL` to 5 or 10
2. Use `mtcnn=False` in FER initialization (already set — faster but less accurate)
3. For Pi: Consider using a lighter model or reduce frame resolution

### Emotion always "neutral"

**Causes**:
- Poor lighting
- Face too far from camera
- Low confidence scores

**Solutions**:
1. Improve lighting
2. Position face closer to camera
3. Lower confidence threshold in `camera.py`

## Performance Notes

### Laptop
- FER inference: ~100-300ms per frame
- Negligible impact with sampling interval ≥ 3

### Raspberry Pi 16GB
- Expected: ~500ms-1s per frame (CPU-only)
- Recommended: `CAMERA_SAMPLE_INTERVAL = 5`
- Consider: TensorFlow Lite for 2-3x speedup

## Next Steps (Phase 3)

- [ ] Raspberry Pi Camera Module integration
- [ ] E-Ink display implementation
- [ ] Optimize for low-power operation
- [ ] Add emotion history visualization
- [ ] Implement crisis detection patterns
