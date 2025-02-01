import requests, json, logging
from files.config import config

logger = logging.getLogger(__name__)

# Neural networks class
class neural_networks:
    
    def _mistral_large_2407(self, prompt: list[dict[str, str]]) -> tuple[str, int, int]|str:
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "top_p": 0.8,
            "max_tokens": 1024,
            "model": "pixtral-12b-2409"
        }
        response = requests.post("https://api.mistral.ai/v1/chat/completions",
                                headers={"Content-Type": "application/json", "Authorization": "Bearer "+ config.mistral_token},
                                json=data)
        response = json.loads(response.text)
        if response.status_code == 200:
            logger.info(f"Mistral large API request was successful, status code: {response.status_code}")
            response = json.loads(response.text)
            return response["choices"][0]["message"]["content"]
        else:
            logger.error(f"Mistral large API request error, status code: {response.status_code}, response text: {response.content}")
            return "Возникла ошибка, попробуйте позже"

    def free_gpt_4o_mini(self, prompt: str) -> tuple[str, int, int]|str:
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "top_p": 0.8,
            "max_tokens": 1024,
            "model": "gpt-4o-mini"
        }
        response = requests.post("https://models.inference.ai.azure.com/chat/completions",
                                headers={"Authorization": config.git_token, "Content-Type" : "application/json"},
                                json=data)
        if response.status_code == 200:
            logger.info(f"GPT 4o mini API request was successful, status code: {response.status_code}")
            response = json.loads(response.text)
            return response["choices"][0]["message"]["content"]
        else:
            logger.error(f"GPT 4o mini API request error, status code: {response.status_code}, response text: {response.content}")
        return self._mistral_large_2407(prompt=prompt) 