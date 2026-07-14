import requests
import json
from typing import List, Dict, Any


class OpenRouterClient:
    """
    Isolated API Interface client. Responsible strictly for authenticating with
    OpenRouter, packaging payloads, handling error streams, and returning raw generation strings.
    """

    def __init__(self, api_key: str, referer: str = "http://localhost:3000", app_title: str = "LoreEngine"):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1/chat/completions"
        self.referer = referer
        self.app_title = app_title

    def generate_completion(self,
                            prompt: str,
                            model: str = "deepseek/deepseek-chat",
                            system_prompt: str = "",
                            temperature: float = 0.85,
                            max_tokens: int = 1024) -> str:
        """
        Submits prompt to OpenRouter endpoint and returns text completion safely.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        return self.generate_chat_completion(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    def generate_chat_completion(self,
                                 messages: List[Dict[str, str]],
                                 model: str = "deepseek/deepseek-chat",
                                 temperature: float = 0.85,
                                 max_tokens: int = 1024) -> str:
        """
        Sends a structured chat message list to OpenRouter and returns the assistant response.

        This is the preferred method for memory-aware roleplay because it preserves
        system prompts, recent conversation turns, and any temporary context blocks.

        Args:
            messages: A list of OpenAI-compatible chat messages.
            model: OpenRouter model identifier.
            temperature: Sampling temperature.
            max_tokens: Maximum response token count.

        Returns:
            The model response content, or a readable error string.
        """
        if not self.api_key or "No API key" in self.api_key:
            return "Error: Missing valid API Key. Please update your Settings tab with an OpenRouter Key."

        # Configure standardized header fields with OpenRouter-specific identifiers
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.referer,
            "X-Title": self.app_title
        }

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            response = requests.post(
                self.base_url,
                headers=headers,
                data=json.dumps(payload),
                timeout=30  # Set a solid timeout so the app doesn't hang indefinitely on weak connections
            )

            # Raise HTTP exceptions if status codes reflect auth or network limits
            response.raise_for_status()

            data = response.json()
            # Extract content from the first response choice
            if "choices" in data and len(data["choices"]) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                return f"Error: Unexpected payload format received from OpenRouter API.\nResponse: {data}"

        except requests.exceptions.RequestException as e:
            # Trap any status, timeout, or DNS connection faults gracefully
            return f"Error connecting to OpenRouter engine: {str(e)}"