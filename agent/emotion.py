"""
Emotional intelligence layer.
Combines sentiment analysis, facial emotion detection, and historical patterns
to build a dynamic mental state model that influences LLM responses.
"""

import logging
from dataclasses import dataclass
from collections import deque
from typing import Optional

from agent.sentiment import SentimentResult
from agent.memory import RetrievedMemory

logger = logging.getLogger(__name__)


@dataclass
class MentalState:
    """Current inferred mental state of the user."""

    sentiment: SentimentResult
    face_emotion: Optional[str] = None
    historical_sentiment_avg: float = 0.0
    emotional_trend: str = "stable"  # "improving", "declining", "stable"
    dominant_emotion: str = "neutral"
    session_turn_count: int = 0

    def to_context_string(self) -> str:
        """Format mental state for injection into the LLM prompt."""
        parts = [
            f"Current sentiment: {self.sentiment.label} "
            f"(intensity: {self.sentiment.intensity:.1f})",
            f"Emotional trend this session: {self.emotional_trend}",
            f"Dominant emotion: {self.dominant_emotion}",
        ]
        if self.face_emotion and self.face_emotion != "unknown":
            parts.append(f"Detected facial emotion: {self.face_emotion}")
        return "\n".join(parts)


class EmotionEngine:
    """Tracks and analyzes emotional state across a conversation session."""

    HISTORY_WINDOW = 10

    def __init__(self):
        self._sentiment_history: deque[float] = deque(maxlen=self.HISTORY_WINDOW)
        self._emotion_history: deque[str] = deque(maxlen=self.HISTORY_WINDOW)
        self._turn_count = 0

    def update(
        self,
        sentiment: SentimentResult,
        face_emotion: Optional[str] = None,
        retrieved_memories: Optional[list[RetrievedMemory]] = None,
    ) -> MentalState:
        """Process new input signals and return updated mental state."""
        self._turn_count += 1
        self._sentiment_history.append(sentiment.compound)

        # Determine dominant emotion from text + face
        effective_emotion = self._resolve_emotion(sentiment, face_emotion)
        self._emotion_history.append(effective_emotion)

        # Calculate historical average and trend
        hist_avg = sum(self._sentiment_history) / len(self._sentiment_history)
        trend = self._compute_trend()

        # Factor in long-term memory patterns
        if retrieved_memories:
            mem_sentiments = [m.sentiment_label for m in retrieved_memories]
            neg_ratio = mem_sentiments.count("negative") / len(mem_sentiments)
            if neg_ratio > 0.6:
                hist_avg -= 0.1  # Weight toward concern

        return MentalState(
            sentiment=sentiment,
            face_emotion=face_emotion,
            historical_sentiment_avg=round(hist_avg, 3),
            emotional_trend=trend,
            dominant_emotion=effective_emotion,
            session_turn_count=self._turn_count,
        )

    def _resolve_emotion(
        self, sentiment: SentimentResult, face_emotion: Optional[str]
    ) -> str:
        """Merge text sentiment and facial emotion into a single label."""
        if face_emotion and face_emotion not in ("unknown", None):
            return face_emotion
        label_map = {
            "positive": "happy",
            "negative": "sad",
            "neutral": "neutral",
        }
        return label_map.get(sentiment.label, "neutral")

    def _compute_trend(self) -> str:
        """Determine if user's emotional state is improving, declining, or stable."""
        if len(self._sentiment_history) < 3:
            return "stable"

        recent = list(self._sentiment_history)
        first_half = recent[: len(recent) // 2]
        second_half = recent[len(recent) // 2 :]

        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        diff = avg_second - avg_first

        if diff > 0.15:
            return "improving"
        elif diff < -0.15:
            return "declining"
        return "stable"
