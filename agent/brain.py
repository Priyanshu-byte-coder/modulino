"""
Central agent brain — orchestrates all modules.
Coordinates LLM, sentiment, memory, and emotion into a unified pipeline.
"""

import logging
import time

from config.config import SYSTEM_PROMPT, EXERCISE_TRIGGER_THRESHOLD, EXERCISE_COOLDOWN_TURNS
from agent.llm import LLMClient
from agent.sentiment import SentimentAnalyzer
from agent.memory import ConversationMemory, MemoryEntry
from agent.emotion import EmotionEngine
from agent.exercises import ExerciseManager

logger = logging.getLogger(__name__)


class AgentBrain:
    """Core agent that coordinates LLM, sentiment, memory, and emotion modules."""

    def __init__(self):
        self.llm = LLMClient()
        self.sentiment = SentimentAnalyzer()
        self.memory = ConversationMemory()
        self.emotion_engine = EmotionEngine()
        self.exercise_manager = ExerciseManager()
        self._conversation_history: list[dict] = []
        self._exercise_state: dict = {"pending": False, "active": False, "current_exercise": None, "step_index": 0}
        logger.info("AgentBrain initialized.")

    def check_systems(self) -> dict[str, bool]:
        """Verify all subsystems are operational."""
        return {
            "llm": self.llm.is_available(),
            "sentiment": True,
            "memory": True,
        }

    def process(self, user_input: str, face_emotion: str | None = None, stream: bool = False):
        """
        Full processing pipeline for a user message.

        1. Check for exercise flow (pending offer or active exercise)
        2. Sentiment analysis
        3. Memory retrieval (RAG)
        4. Emotional state update
        5. Offer exercise if needed
        6. LLM response generation
        7. Memory storage
        """
        # 1. Handle exercise flow if active
        exercise_response = self._handle_exercise_flow(user_input)
        if exercise_response:
            return exercise_response if not stream else self._stream_response(exercise_response)
        
        # 2. Analyze sentiment
        sentiment_result = self.sentiment.analyze(user_input)
        logger.info("Sentiment: %s", sentiment_result)

        # 3. Retrieve relevant memories (RAG)
        memories = self.memory.retrieve(user_input)
        memory_context = self._format_memories(memories)

        # 4. Update emotional state
        mental_state = self.emotion_engine.update(
            sentiment=sentiment_result,
            face_emotion=face_emotion,
            retrieved_memories=memories,
            exercise_threshold=EXERCISE_TRIGGER_THRESHOLD,
        )
        
        # 5. Check if we should offer an exercise
        if mental_state.needs_exercise and self.exercise_manager.should_offer_exercise(
            mental_state.session_turn_count, EXERCISE_COOLDOWN_TURNS
        ):
            self._exercise_state["pending"] = True
            self.exercise_manager.mark_exercise_offered(mental_state.session_turn_count)
            offer_message = self.exercise_manager.format_exercise_offer()
            logger.info("Offering mental exercise to user")
            return offer_message if not stream else self._stream_response(offer_message)

        # 6. Build prompt and generate response
        system_prompt = self._build_system_prompt(mental_state, memory_context)
        self._conversation_history.append({"role": "user", "content": user_input})

        messages = [{"role": "system", "content": system_prompt}] + self._conversation_history[-4:]
        
        if stream:
            response_generator = self.llm.chat(messages, stream_output=True)
            
            def wrapped_generator():
                full_response = []
                for token in response_generator:
                    full_response.append(token)
                    yield token
                    
                final_response = "".join(full_response).strip()
                self._conversation_history.append({"role": "assistant", "content": final_response})
                
                # 7. Store in long-term memory
                self.memory.store(
                    MemoryEntry(
                        user_message=user_input,
                        assistant_response=final_response,
                        sentiment_label=sentiment_result.label,
                        sentiment_score=sentiment_result.compound,
                        emotion=mental_state.dominant_emotion,
                        timestamp=time.time(),
                    )
                )
            return wrapped_generator()
        else:
            response = self.llm.chat(messages)

            self._conversation_history.append({"role": "assistant", "content": response})

            # 7. Store in long-term memory
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

    def _handle_exercise_flow(self, user_input: str) -> str | None:
        """Handle exercise offer acceptance/rejection (terminal CLI mode).
        
        In the web UI, exercises are fully managed by the frontend via API
        endpoints (/api/trigger_exercise, /api/exercise/start). The chat_stream
        endpoint intercepts exercise offers and emits structured SSE events.
        
        This method is only meaningful for the terminal CLI (main.py) where the
        user types 'yes' or 'skip' directly.
        """
        user_lower = user_input.lower().strip()
        
        # If exercise is active (frontend-driven), don't intercept — let normal chat continue
        if self._exercise_state["active"]:
            self._exercise_state["active"] = False
            self._exercise_state["current_exercise"] = None
            return None
        
        # Check if user is responding to a pending exercise offer (terminal mode)
        if self._exercise_state["pending"]:
            if any(word in user_lower for word in ["yes", "sure", "okay", "ok", "let's do it", "lets do it", "do it", "please"]):
                exercise = self.exercise_manager.get_random_exercise()
                self._exercise_state["pending"] = False
                logger.info(f"Starting exercise (terminal): {exercise.name}")
                steps_text = "\n\n".join(s.text for s in exercise.steps)
                return steps_text
            
            elif any(word in user_lower for word in ["no", "skip", "not now", "later", "nah", "pass"]):
                self._exercise_state["pending"] = False
                logger.info("User declined exercise")
                return "That's okay! I'm here whenever you need to talk. What's on your mind?"
            
            else:
                # Unclear response — clear pending and let message pass through to normal LLM
                self._exercise_state["pending"] = False
                logger.info("Exercise offer ignored, continuing normal chat")
                return None
        
        return None
    
    def _stream_response(self, text: str):
        """Convert a static text response into a generator for streaming."""
        def generator():
            for char in text:
                yield char
        return generator()
