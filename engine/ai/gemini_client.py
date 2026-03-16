import time
from google import genai
from google.genai import types

from engine.config import Config
from engine.utils.logger import get_logger

logger = get_logger("GeminiClient")


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model = "gemini-2.5-flash"
        self.max_retries = 3
        self.retry_delay = 2

    def ask(self, prompt: str, max_tokens: int = 8192) -> str:
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        max_output_tokens=max_tokens,
                        temperature=0.7,
                    ),
                )
                return response.text
            except Exception as e:
                logger.warning(f"Gemini attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay * attempt)
                else:
                    logger.error(f"Gemini failed after {self.max_retries} attempts")
                    raise
        return ""
