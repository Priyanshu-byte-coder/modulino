"""
Camera abstraction layer.
Laptop webcam implementation for development.
Replace with Raspberry Pi camera module for deployment — only this file changes.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from config.config import CAMERA_ENABLED, CAMERA_INDEX

logger = logging.getLogger(__name__)


class BaseCamera(ABC):
    """Abstract camera interface."""

    @abstractmethod
    def capture_emotion(self) -> Optional[str]: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def release(self) -> None: ...

    @abstractmethod
    def capture_frame(self) -> Optional["numpy.ndarray"]: ...

    @abstractmethod
    def capture_snapshot_with_overlay(self) -> tuple[Optional[bytes], Optional[str]]: ...


class WebcamCamera(BaseCamera):
    """Laptop webcam implementation with FER emotion detection."""

    def __init__(self):
        self._cap = None
        self._detector = None
        self._initialized = False
        
        if CAMERA_ENABLED:
            self._initialize()

    def _initialize(self) -> None:
        """Lazy initialization of camera and FER detector."""
        try:
            import cv2

            logger.info(f"Attempting to open camera at index {CAMERA_INDEX}")
            self._cap = cv2.VideoCapture(CAMERA_INDEX)
            if not self._cap.isOpened():
                logger.warning(f"Failed to open webcam at index {CAMERA_INDEX}.")
                self._cap = None
                return

            # Camera initialized successfully
            self._initialized = True
            logger.info(f"Webcam initialized on camera index {CAMERA_INDEX}.")
            
            # Try to initialize FER (optional)
            try:
                from fer import FER
                self._detector = FER(mtcnn=False)
                logger.info("FER emotion detection enabled.")
            except ImportError as e:
                logger.warning("FER not available (missing dependency): %s. Camera will work without emotion detection.", e)
                self._detector = None
            except Exception as e:
                logger.warning("FER initialization failed: %s. Camera will work without emotion detection.", e)
                self._detector = None
                
        except ImportError as e:
            logger.error("OpenCV not available: %s", e)
            self._cap = None
            self._detector = None
            self._initialized = False
        except Exception as e:
            logger.error("Camera initialization failed: %s", e)
            self._cap = None
            self._detector = None
            self._initialized = False

    def capture_emotion(self) -> Optional[str]:
        """Capture frame and detect dominant emotion. Returns emotion label or None."""
        if not CAMERA_ENABLED or not self._initialized or self._detector is None:
            return None

        try:
            import cv2

            ret, frame = self._cap.read()
            if not ret or frame is None:
                logger.warning("Failed to capture frame from webcam.")
                return None

            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            result = self._detector.detect_emotions(rgb_frame)
            
            if not result or len(result) == 0:
                logger.warning("No face detected in frame. Make sure your face is visible to the camera.")
                return None

            emotions = result[0]["emotions"]
            dominant_emotion = max(emotions, key=emotions.get)
            confidence = emotions[dominant_emotion]

            if confidence < 0.3:
                logger.warning("Low confidence emotion detection: %s (%.2f). Try better lighting or move closer.", dominant_emotion, confidence)
                return None

            logger.info("Detected emotion: %s (confidence: %.2f)", dominant_emotion, confidence)
            return dominant_emotion

        except Exception as e:
            logger.error("Emotion capture error: %s", e)
            return None

    def is_available(self) -> bool:
        if not CAMERA_ENABLED:
            return False
        if self._initialized and self._cap is not None:
            return self._cap.isOpened()
        
        try:
            import cv2

            cap = cv2.VideoCapture(CAMERA_INDEX)
            ok = cap.isOpened()
            cap.release()
            return ok
        except ImportError:
            logger.warning("opencv-python not installed; camera unavailable.")
            return False

    def capture_frame(self):
        """Capture a single raw frame from the camera. Returns frame or None."""
        if not self._initialized or self._cap is None:
            return None
        try:
            import cv2
            ret, frame = self._cap.read()
            if not ret or frame is None:
                return None
            return frame
        except Exception as e:
            logger.error("Frame capture error: %s", e)
            return None

    def capture_snapshot_with_overlay(self) -> tuple[Optional[bytes], Optional[str]]:
        """Capture frame, run emotion detection, draw overlay, return (jpeg_bytes, emotion)."""
        if not self._initialized or self._cap is None:
            return None, None
        try:
            import cv2
            ret, frame = self._cap.read()
            if not ret or frame is None:
                return None, None

            emotion = None
            if self._detector is not None:
                try:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    result = self._detector.detect_emotions(rgb_frame)
                    if result and len(result) > 0:
                        emotions = result[0]["emotions"]
                        emotion = max(emotions, key=emotions.get)
                        confidence = emotions[emotion]
                        box = result[0]["box"]
                        x, y, w, h = box
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        text = f"{emotion}: {confidence:.2f}"
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        text_size = cv2.getTextSize(text, font, 0.6, 2)[0]
                        cv2.rectangle(frame, (x, y - 30), (x + text_size[0] + 10, y), (0, 255, 0), -1)
                        cv2.putText(frame, text, (x + 5, y - 10), font, 0.6, (0, 0, 0), 2)
                except Exception as e:
                    logger.warning("Emotion detection failed during snapshot: %s", e)

            _, buffer = cv2.imencode('.jpg', frame)
            return buffer.tobytes(), emotion
        except Exception as e:
            logger.error("Snapshot capture error: %s", e)
            return None, None

    def release(self) -> None:
        if self._cap is not None:
            self._cap.release()
            self._cap = None
        self._detector = None
        self._initialized = False
        logger.info("Camera released.")


def create_camera() -> BaseCamera:
    """Factory function — returns the appropriate camera for the current config."""
    return WebcamCamera()
