"""
Camera abstraction layer.
Laptop webcam implementation for development.
Replace with Raspberry Pi camera module for deployment — only this file changes.
"""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from config.config import CAMERA_ENABLED

logger = logging.getLogger(__name__)


class BaseCamera(ABC):
    """Abstract camera interface."""

    @abstractmethod
    def capture_emotion(self) -> Optional[str]: ...

    @abstractmethod
    def is_available(self) -> bool: ...

    @abstractmethod
    def release(self) -> None: ...


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
            from fer import FER

            self._cap = cv2.VideoCapture(0)
            if not self._cap.isOpened():
                logger.warning("Failed to open webcam.")
                self._cap = None
                return

            self._detector = FER(mtcnn=False)
            self._initialized = True
            logger.info("Webcam emotion detection initialized (FER).")
        except ImportError as e:
            logger.warning("FER or OpenCV not available: %s", e)
            self._cap = None
            self._detector = None
        except Exception as e:
            logger.error("Camera initialization failed: %s", e)
            self._cap = None
            self._detector = None

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

            cap = cv2.VideoCapture(0)
            ok = cap.isOpened()
            cap.release()
            return ok
        except ImportError:
            logger.warning("opencv-python not installed; camera unavailable.")
            return False

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
