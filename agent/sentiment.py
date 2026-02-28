"""
Offline sentiment analysis module using VADER.
Lightweight, CPU-only, suitable for Raspberry Pi deployment.
"""

import logging
from dataclasses import dataclass

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config.config import SENTIMENT_THRESHOLDS

logger = logging.getLogger(__name__)


@dataclass
class SentimentResult:
    """Structured sentiment analysis output."""

    label: str        # "positive", "negative", "neutral"
    compound: float   # -1.0 to 1.0
    intensity: float  # 0.0 to 1.0 (absolute strength)
    scores: dict      # Raw VADER scores

    def __str__(self) -> str:
        return f"{self.label} (compound={self.compound:.2f}, intensity={self.intensity:.2f})"


class SentimentAnalyzer:
    """VADER-based sentiment analyzer for conversational text."""

    def __init__(self):
        self._analyzer = SentimentIntensityAnalyzer()
        self._thresholds = SENTIMENT_THRESHOLDS
        logger.info("Sentiment analyzer initialized (VADER).")

    def analyze(self, text: str) -> SentimentResult:
        """Analyze sentiment of the given text and return a structured result."""
        if not text or not text.strip():
            return SentimentResult(
                label="neutral", compound=0.0, intensity=0.0, scores={}
            )

        scores = self._analyzer.polarity_scores(text)
        compound = scores["compound"]

        if compound >= self._thresholds["positive"]:
            label = "positive"
        elif compound <= self._thresholds["negative"]:
            label = "negative"
        else:
            label = "neutral"

        intensity = abs(compound)

        return SentimentResult(
            label=label,
            compound=compound,
            intensity=intensity,
            scores=scores,
        )
