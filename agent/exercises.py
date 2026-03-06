"""
Mental wellbeing exercises for stress relief and mood improvement.
Quick 30-second exercises optimized for Raspberry Pi performance.

Each exercise step has:
  - text: instruction shown to the user
  - duration: seconds for this step (0 = brief display ~2s, >0 = countdown timer)
  - step_type: "text" (auto-advance after delay) or "timer" (show countdown circle)
"""

import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ExerciseStep:
    """A single step in an exercise."""
    text: str
    duration: int = 0        # 0 = auto-advance after ~3s, >0 = show timer
    step_type: str = "text"  # "text" or "timer"


@dataclass
class Exercise:
    """A guided mental exercise."""
    name: str
    category: str       # "breathing", "grounding", "gratitude", "mindfulness"
    icon: str            # emoji for the UI card
    description: str     # short description for the selection card
    steps: list[ExerciseStep] = field(default_factory=list)
    duration_seconds: int = 0

    def to_dict(self) -> dict:
        """Serialize for JSON API responses."""
        return {
            "name": self.name,
            "category": self.category,
            "icon": self.icon,
            "description": self.description,
            "duration_seconds": self.duration_seconds,
            "steps": [
                {"text": s.text, "duration": s.duration, "step_type": s.step_type}
                for s in self.steps
            ],
        }


# ---------------------------------------------------------------------------
# Exercise library – all under 30 seconds
# ---------------------------------------------------------------------------

EXERCISES = [
    Exercise(
        name="Box Breathing",
        category="breathing",
        icon="🌬️",
        description="4-4-4-4 breathing pattern to calm your mind",
        duration_seconds=24,
        steps=[
            ExerciseStep("Let's do Box Breathing together. Get comfortable.", 3, "text"),
            ExerciseStep("Breathe IN slowly...", 4, "timer"),
            ExerciseStep("HOLD your breath...", 4, "timer"),
            ExerciseStep("Breathe OUT slowly...", 4, "timer"),
            ExerciseStep("HOLD gently...", 4, "timer"),
            ExerciseStep("Wonderful! You did great. How do you feel now?", 0, "text"),
        ],
    ),
    Exercise(
        name="Calming Breath",
        category="breathing",
        icon="🍃",
        description="Inhale 4s, exhale 6s — twice",
        duration_seconds=26,
        steps=[
            ExerciseStep("Let's try a calming breath. Ready?", 3, "text"),
            ExerciseStep("Breathe IN through your nose...", 4, "timer"),
            ExerciseStep("Breathe OUT through your mouth...", 6, "timer"),
            ExerciseStep("Once more — breathe IN...", 4, "timer"),
            ExerciseStep("And breathe OUT...", 6, "timer"),
            ExerciseStep("Perfect. Notice how your body feels more relaxed.", 0, "text"),
        ],
    ),
    Exercise(
        name="5-4-3-2-1 Grounding",
        category="grounding",
        icon="🌍",
        description="Ground yourself using your five senses",
        duration_seconds=30,
        steps=[
            ExerciseStep("Let's ground ourselves in the present moment.", 3, "text"),
            ExerciseStep("Look around — name 5 things you can SEE.", 5, "text"),
            ExerciseStep("Now notice 4 things you can FEEL or touch.", 5, "text"),
            ExerciseStep("Listen — 3 things you can HEAR right now.", 5, "text"),
            ExerciseStep("2 things you can SMELL.", 4, "text"),
            ExerciseStep("And 1 thing you can TASTE.", 3, "text"),
            ExerciseStep("You're here. You're present. You're safe.", 0, "text"),
        ],
    ),
    Exercise(
        name="Quick Gratitude",
        category="gratitude",
        icon="🙏",
        description="Reflect on one thing you're grateful for",
        duration_seconds=20,
        steps=[
            ExerciseStep("Let's shift focus to something positive.", 3, "text"),
            ExerciseStep("Think of one thing you're grateful for today.", 5, "text"),
            ExerciseStep("It can be small — a warm drink, a kind word, or this moment.", 5, "text"),
            ExerciseStep("Hold that thought and let it warm you...", 4, "text"),
            ExerciseStep("Gratitude helps us find light even in hard times.", 0, "text"),
        ],
    ),
    Exercise(
        name="Body Scan",
        category="mindfulness",
        icon="🧘",
        description="Release tension from head to toe",
        duration_seconds=25,
        steps=[
            ExerciseStep("Let's do a quick body check-in.", 3, "text"),
            ExerciseStep("Notice your shoulders — let them drop and relax.", 5, "text"),
            ExerciseStep("Unclench your jaw if it's tight.", 4, "text"),
            ExerciseStep("Take a deep breath — feel your chest expand.", 5, "text"),
            ExerciseStep("Wiggle your toes and feel the ground beneath you.", 4, "text"),
            ExerciseStep("You're taking care of yourself right now.", 0, "text"),
        ],
    ),
    Exercise(
        name="Tension Release",
        category="mindfulness",
        icon="💪",
        description="Squeeze-and-release muscle relaxation",
        duration_seconds=25,
        steps=[
            ExerciseStep("Let's release some physical tension.", 3, "text"),
            ExerciseStep("Squeeze your fists tight...", 3, "timer"),
            ExerciseStep("Now release! Feel the difference.", 3, "text"),
            ExerciseStep("Scrunch shoulders to your ears...", 3, "timer"),
            ExerciseStep("And drop them. Ahhh.", 3, "text"),
            ExerciseStep("Tense your whole body...", 3, "timer"),
            ExerciseStep("And let it all go.", 3, "text"),
            ExerciseStep("Take a deep breath. You did great.", 0, "text"),
        ],
    ),
]


class ExerciseManager:
    """Manages exercise selection and state."""

    def __init__(self):
        self._last_exercise_turn: Optional[int] = None
        self._last_exercise_name: Optional[str] = None

    def should_offer_exercise(self, current_turn: int, cooldown_turns: int) -> bool:
        """Check if enough turns have passed since last exercise offer."""
        if self._last_exercise_turn is None:
            return True
        return (current_turn - self._last_exercise_turn) >= cooldown_turns

    def get_random_exercise(self) -> Exercise:
        """Select a random exercise, avoiding the last one if possible."""
        available = [e for e in EXERCISES if e.name != self._last_exercise_name]
        if not available:
            available = EXERCISES
        exercise = random.choice(available)
        self._last_exercise_name = exercise.name
        return exercise

    def get_exercise_by_name(self, name: str) -> Optional[Exercise]:
        """Find an exercise by its name (case-insensitive)."""
        for e in EXERCISES:
            if e.name.lower() == name.lower():
                return e
        return None

    def get_all_exercises(self) -> list[dict]:
        """Return all exercises as dicts for the API."""
        return [e.to_dict() for e in EXERCISES]

    def mark_exercise_offered(self, turn: int):
        """Record that an exercise was offered at this turn."""
        self._last_exercise_turn = turn

    def format_exercise_offer(self) -> str:
        """Format the exercise offer message."""
        return (
            "I notice you might be feeling stressed. "
            "Would you like to try a quick 30-second exercise to help? "
            "Just say 'yes' or 'let's do it' if you'd like, or 'skip' to continue talking."
        )
