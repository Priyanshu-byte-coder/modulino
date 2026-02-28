"""
Central agent brain — orchestrates all modules.
Coordinates LLM, sentiment, memory, and emotion into a unified pipeline.
"""

import logging
import time

from config.config import SYSTEM_PROMPT
from agent.llm import LLMClient
from agent.sentiment import SentimentAnalyzer
from agent.memory import ConversationMemory, MemoryEntry
from agent.emotion import EmotionEngine

logger = logging.getLogger(__name__)


class AgentBrain:
    """Core agent that coordinates LLM, sentiment, memory, and emotion modules."""

    def __init__(self):
        self.llm = LLMClient()
        self.sentiment = SentimentAnalyzer()
        self.memory = ConversationMemory()
        self.emotion_engine = EmotionEngine()
        self._conversation_history: list[dict] = []
        logger.info("AgentBrain initialized.")

    def check_systems(self) -> dict[str, bool]:
        """Verify all subsystems are operational."""
        return {
            "llm": self.llm.is_available(),
            "sentiment": True,
            "memory": True,
        }

    def process(self, user_input: str, face_emotion: str | None = None) -> str:
        """
        Full processing pipeline for a user message.

        1. Sentiment analysis
        2. Memory retrieval (RAG)
        3. Emotional state update
        4. LLM response generation
        5. Memory storage
        """
        # 1. Analyze sentiment
        sentiment_result = self.sentiment.analyze(user_input)
        logger.info("Sentiment: %s", sentiment_result)

        # 2. Retrieve relevant memories (RAG)
        memories = self.memory.retrieve(user_input)
        memory_context = self._format_memories(memories)

        # 3. Update emotional state
        mental_state = self.emotion_engine.update(
            sentiment=sentiment_result,
            face_emotion=face_emotion,
            retrieved_memories=memories,
        )

        # 4. Build prompt and generate response
        system_prompt = self._build_system_prompt(mental_state, memory_context)
        self._conversation_history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": system_prompt}] + self._conversation_history[-4:]
        response = self.llm.chat(messages)

        self._conversation_history.append({"role": "assistant", "content": response})

        # 5. Store in long-term memory
        self.memory.store(
            MemoryEntry(
                user_message=user_input,
                assistant_response=response,
                sentiment_label=sentiment_result.label,
                sentiment_score=sentiment_result.compound,
                emotion=mental_state.dominant_emotion,
                timestamp=time.time(),
            )
        )

        return response

    def _build_system_prompt(self, mental_state, memory_context: str) -> str:
        """Construct a compact system prompt for CPU inference."""
        parts = [SYSTEM_PROMPT]

        parts.append(f"\nUser mood: {mental_state.dominant_emotion}.")

        if mental_state.emotional_trend == "declining":
            parts.append("Be extra gentle.")

        if memory_context:
            parts.append(f"\nContext:\n{memory_context}")

        return " ".join(parts)

    def _format_memories(self, memories) -> str:
        """Format retrieved memories into a context string for the LLM."""
        if not memories:
            return ""
        lines = []
        for i, m in enumerate(memories[:2], 1):  # Top 2 most relevant
            lines.append(
                f"{i}. User said: \"{m.user_message[:80]}\""
            )
        return "\n".join(lines)
