import requests
from app.core.config import settings


class OllamaClient:
    def __init__(self):
        self.generate_url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate"

    def generate(self, prompt: str, model: str | None = None) -> str:
        payload = {
            "model": model or settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": settings.OLLAMA_TEMPERATURE,
                "num_ctx": settings.OLLAMA_NUM_CTX,
                "num_predict": settings.OLLAMA_NUM_PREDICT,
                "top_k": settings.OLLAMA_TOP_K,
                "top_p": settings.OLLAMA_TOP_P,
            }
        }

        response = requests.post(
            self.generate_url,
            json=payload,
            timeout=settings.OLLAMA_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")