"""
Display abstraction layer.
Terminal implementation for laptop development.
Replace with E-Ink rendering for Raspberry Pi deployment — only this file changes.
"""

import os
import textwrap
from abc import ABC, abstractmethod

from config.config import DISPLAY_MODE, TERMINAL_WIDTH


class BaseDisplay(ABC):
    """Abstract display interface — swap implementations for different hardware."""

    @abstractmethod
    def show_message(self, sender: str, message: str) -> None: ...

    @abstractmethod
    def show_status(self, status: str) -> None: ...

    @abstractmethod
    def show_welcome(self) -> None: ...

    @abstractmethod
    def clear(self) -> None: ...

    @abstractmethod
    def show_emotion(self, emotion: str) -> None: ...


class TerminalDisplay(BaseDisplay):
    """Rich terminal output simulating an E-Ink display."""

    def __init__(self, width: int = TERMINAL_WIDTH):
        self.width = width

    def show_message(self, sender: str, message: str) -> None:
        prefix = "You" if sender == "user" else "Maya"
        wrapped = textwrap.fill(message, width=self.width - 4)
        indent = "  "

        if sender == "user":
            print(f"\n  [{prefix}]")
            for line in wrapped.split("\n"):
                print(f"{indent}> {line}")
        else:
            print(f"\n  [{prefix}]")
            for line in wrapped.split("\n"):
                print(f"{indent}  {line}")
        print()

    def show_status(self, status: str) -> None:
        print(f"  ... {status}")

    def show_welcome(self) -> None:
        border = "=" * self.width
        print(f"\n{border}")
        print("💙 Maya - Your Wellbeing Companion 💙".center(self.width + 4))
        print(f"{border}")
        print()
        print("  Hey there! I'm Maya, your supportive friend 😊")
        print("  Share whatever's on your mind - I'm here to listen")
        print("  Everything stays private and offline on your device 🔒")
        print()
        print("  Type 'quit' or 'exit' when you're ready to go")
        print()

    def clear(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")

    def show_emotion(self, emotion: str) -> None:
        emotion_icons = {
            "happy": "😊",
            "sad": "😢",
            "angry": "😠",
            "fear": "😨",
            "surprise": "😲",
            "neutral": "😐",
            "disgust": "🤢",
        }
        icon = emotion_icons.get(emotion, "🤔")
        print(f"  📷 Detected: {emotion} {icon}")


def create_display() -> BaseDisplay:
    """Factory function — returns the appropriate display for the current config."""
    if DISPLAY_MODE == "eink":
        raise NotImplementedError(
            "E-Ink display not yet implemented. Set DISPLAY_MODE=terminal."
        )
    return TerminalDisplay()
