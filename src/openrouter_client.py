"""
OpenRouter API Client
Handles communication with OpenRouter API for AI generation
"""

import os
import requests
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class OpenRouterClient:
    """Client for OpenRouter API"""

    def __init__(self, api_key: Optional[str] = None, model: str = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.model = model or os.getenv('AI_MODEL', 'anthropic/claude-3-haiku')
        self.base_url = "https://openrouter.ai/api/v1"

        if not self.api_key:
            raise ValueError("OpenRouter API key required. Get one at https://openrouter.ai")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate response using OpenRouter"""

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 4000,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120
            )

            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                raise Exception(f"OpenRouter API error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            raise Exception("OpenRouter API request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            raise Exception("Cannot connect to OpenRouter API. Check your internet connection.")
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    def test_connection(self) -> bool:
        """Test OpenRouter API connection"""
        try:
            response = self.generate("Test connection", "Reply with 'OK'")
            return "OK" in response.upper()
        except Exception:
            return False