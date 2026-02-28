"""
LLM integration module using Ollama (local inference).
Communicates with Ollama's REST API for fully offline operation.
"""

import json
import logging
from typing import Optional

import requests

from config.config import (
    OLLAMA_BASE_URL,
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    LLM_NUM_CTX,
    LLM_NUM_THREAD,
    LLM_TIMEOUT,
    LLM_STOP_SEQUENCES,
)

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for local LLM inference via Ollama."""

    def __init__(
        self,
        base_url: str = OLLAMA_BASE_URL,
        model: str = LLM_MODEL,
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def is_available(self) -> bool:
        """Check if Ollama server is running and the configured model is loaded."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                available = any(self.model in m for m in models)
                if not available:
                    logger.warning(
                        "Model '%s' not found. Available: %s", self.model, models
                    )
                return available
            return False
        except requests.ConnectionError:
            logger.error("Ollama server is not running.")
            return False

    def generate(self, prompt: str, system: str = "") -> str:
        """Single-shot generation via /api/generate with streaming."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
                "num_ctx": LLM_NUM_CTX,
                "num_thread": LLM_NUM_THREAD,
                "stop": LLM_STOP_SEQUENCES,
            },
        }
        try:
            resp = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=LLM_TIMEOUT,
                stream=True,
            )
            resp.raise_for_status()
            full_response = []
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("response", "")
                    full_response.append(token)
                    if chunk.get("done", False):
                        break
            return "".join(full_response).strip()
        except requests.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return "[Error: LLM server unavailable. Please start Ollama.]"
        except requests.Timeout:
            logger.error("LLM request timed out.")
            return "[Error: LLM request timed out.]"
        except Exception as e:
            logger.error("LLM generation error: %s", e)
            return f"[Error: {e}]"

    def chat(self, messages: list[dict]) -> str:
        """Chat-style generation via /api/chat with streaming."""
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
                "num_ctx": LLM_NUM_CTX,
                "num_thread": LLM_NUM_THREAD,
                "stop": LLM_STOP_SEQUENCES,
            },
        }
        try:
            resp = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=LLM_TIMEOUT,
                stream=True,
            )
            resp.raise_for_status()
            full_response = []
            for line in resp.iter_lines():
                if line:
                    chunk = json.loads(line)
                    token = chunk.get("message", {}).get("content", "")
                    full_response.append(token)
                    if chunk.get("done", False):
                        break
            return "".join(full_response).strip()
        except requests.ConnectionError:
            logger.error("Cannot connect to Ollama. Is it running?")
            return "[Error: LLM server unavailable. Please start Ollama.]"
        except requests.Timeout:
            logger.error("LLM request timed out.")
            return "[Error: LLM request timed out.]"
        except Exception as e:
            logger.error("LLM chat error: %s", e)
            return f"[Error: {e}]"
