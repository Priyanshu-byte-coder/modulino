"""
Quick camera diagnostic script.
Run this to test if FER and webcam are working correctly.
"""

import sys

print("=" * 60)
print("Camera & FER Diagnostic Test")
print("=" * 60)

# Test 1: Check if camera can be opened
print("\n[1/4] Testing webcam access...")
try:
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        print("✓ Webcam opened successfully")
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✓ Frame captured: {frame.shape}")
        else:
            print("✗ Failed to capture frame")
            cap.release()
            sys.exit(1)
        cap.release()
    else:
        print("✗ Failed to open webcam")
        print("  - Check if another app is using the camera")
        print("  - Check Windows camera permissions")
        sys.exit(1)
except ImportError:
    print("✗ OpenCV not installed")
    print("  Run: pip install opencv-python")
    sys.exit(1)

# Test 2: Check FER installation
print("\n[2/4] Testing FER installation...")
try:
    from fer import FER
    print("✓ FER library imported successfully")
except ImportError as e:
    print(f"✗ FER import failed: {e}")
    print("\nDiagnosing issue...")
    
    # Check if fer package exists
    try:
        import fer
        print(f"  - fer package found at: {fer.__file__}")
        print(f"  - fer version: {fer.__version__ if hasattr(fer, '__version__') else 'unknown'}")
    except ImportError:
        print("  - fer package not found in Python path")
    
    # Check dependencies
    missing = []
    for dep in ['tensorflow', 'torch', 'torchvision']:
        try:
            __import__(dep)
        except ImportError:
            missing.append(dep)
    
    if missing:
        print(f"  - Missing dependencies: {', '.join(missing)}")
    
    print("\n  Try: pip uninstall fer -y && pip install fer tensorflow")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Initialize FER detector
print("\n[3/4] Initializing FER detector...")
try:
    detector = FER(mtcnn=False)
    print("✓ FER detector initialized")
except Exception as e:
    print(f"✗ FER initialization failed: {e}")
    sys.exit(1)

# Test 4: Capture and detect emotion
print("\n[4/4] Testing emotion detection...")
print("  Position your face in front of the camera...")
print("  Capturing in 3 seconds...")

import time
time.sleep(3)

try:
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print("✗ Failed to capture test frame")
        sys.exit(1)
    
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = detector.detect_emotions(rgb_frame)
    
    if not result or len(result) == 0:
        print("✗ No face detected")
        print("\nTroubleshooting:")
        print("  - Ensure your face is clearly visible")
        print("  - Check lighting (avoid backlighting)")
        print("  - Move closer to the camera")
        print("  - Make sure camera is not covered")
    else:
        print(f"✓ Detected {len(result)} face(s)")
        emotions = result[0]["emotions"]
        print("\nEmotion scores:")
        for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
            bar = "█" * int(score * 20)
            print(f"  {emotion:10s} {score:.3f} {bar}")
        
        dominant = max(emotions, key=emotions.get)
        confidence = emotions[dominant]
        
        print(f"\n✓ Dominant emotion: {dominant} (confidence: {confidence:.2f})")
        
        if confidence < 0.3:
            print("  ⚠️  Low confidence - improve lighting or face visibility")

except Exception as e:
    print(f"✗ Emotion detection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed! Camera is working correctly.")
print("=" * 60)
print("\nYou can now use the main app with CAMERA_ENABLED=true")
