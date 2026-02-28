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

        messages = [{"role": "system", "content": system_prompt}] + self._conversation_history[-10:]
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
        """Construct the full system prompt with emotional context."""
        parts = [SYSTEM_PROMPT]
        
        # Add critical instruction to prevent context leakage
        parts.append(
            "\n\n**IMPORTANT**: The following context is for YOUR INTERNAL USE ONLY. "
            "NEVER include any of the sections below (User Emotional Context, Past Conversations, Notes) "
            "in your response to the user. Respond naturally as a compassionate companion without "
            "mentioning sentiment scores, emotion labels, or metadata."
        )
        
        parts.append(
            f"\n\n=== INTERNAL CONTEXT (DO NOT MENTION IN RESPONSE) ===\n"
            f"User Emotional State:\n{mental_state.to_context_string()}"
        )

        if memory_context:
            parts.append(
                f"\n\nRelevant Past Conversations (USE THESE FOR CONTINUITY):\n"
                f"The following are the most relevant past exchanges with this user. "
                f"Use them to maintain conversational continuity, remember their name, "
                f"recall previous topics, and show you're paying attention.\n\n"
                f"{memory_context}"
            )

        # Tone guidance based on emotional state
        if mental_state.emotional_trend == "declining":
            parts.append(
                "\n\nGuidance: The user's mood appears to be declining. "
                "Be extra gentle, validating, and supportive."
            )
        elif mental_state.dominant_emotion in ("sad", "fear", "angry"):
            parts.append(
                "\n\nGuidance: The user seems distressed. Prioritize empathy and "
                "active listening before offering any suggestions."
            )
        
        parts.append("\n=== END INTERNAL CONTEXT ===\n")

        return "\n".join(parts)

    def _format_memories(self, memories) -> str:
        """Format retrieved memories into a context string for the LLM."""
        if not memories:
            return ""
        lines = []
        for i, m in enumerate(memories[:5], 1):  # Top 5 most relevant
            lines.append(
                f"{i}. User: \"{m.user_message[:200]}\"\n"
                f"   You responded: \"{m.assistant_response[:200]}\"\n"
                f"   (Context: {m.sentiment_label} mood, {m.emotion} emotion)"
            )
        return "\n".join(lines)
