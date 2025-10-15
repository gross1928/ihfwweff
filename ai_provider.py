"""
Модуль для работы с OpenRouter API
"""

import aiohttp
from typing import List, Dict
import config


class OpenRouterProvider:
    """Провайдер для OpenRouter API (агрегатор моделей)"""
    
    # Популярные uncensored модели на OpenRouter
    MODELS = {
        "mythomax": "gryphe/mythomax-l2-13b",
        "nous-hermes": "nousresearch/hermes-3-llama-3.1-70b",  # Hermes 3 70B
        "nous-hermes-8b": "nousresearch/hermes-2-pro-llama-3-8b",  # Hermes 2 Pro 8B (дешевле)
        "hermes-4": "nousresearch/hermes-4-70b",  # Hermes 4 70B (новейшая)
        "llama-70b": "meta-llama/llama-2-70b-chat",
        "dolphin": "cognitivecomputations/dolphin-mixtral-8x7b"
    }
    
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        model_name = config.MODEL_NAME
        # Пробуем найти модель в словаре коротких имен
        self.model = self.MODELS.get(model_name, model_name)
    
    async def generate_response(self, system_prompt: str, conversation_history: List[Dict], user_message: str) -> str:
        """Генерирует ответ через OpenRouter API"""
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/sexting-bot",  # Опционально
            "X-Title": "Sexting Bot"  # Опционально
        }
        
        # Формируем сообщения
        messages = [{"role": "system", "content": system_prompt}]
        messages.extend(conversation_history[-config.MAX_HISTORY_LENGTH:])
        messages.append({"role": "user", "content": user_message})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.TEMPERATURE,
            "top_p": 0.9,
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as response:
                result = await response.json()
                
                # Обработка ошибок
                if "error" in result:
                    error_msg = result["error"].get("message", "Unknown error")
                    return f"Извините, произошла ошибка: {error_msg}"
                
                # Извлекаем ответ
                try:
                    return result["choices"][0]["message"]["content"]
                except (KeyError, IndexError):
                    return "Извините, не удалось получить ответ от модели."


def get_ai_provider() -> OpenRouterProvider:
    """Возвращает OpenRouter провайдер"""
    if not config.OPENROUTER_API_KEY or config.OPENROUTER_API_KEY == "your_openrouter_key_here":
        print("⚠️ ВНИМАНИЕ: OPENROUTER_API_KEY не настроен в .env файле!")
        print("Получите ключ на https://openrouter.ai/keys")
    
    return OpenRouterProvider()

