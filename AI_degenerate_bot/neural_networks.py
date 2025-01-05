import requests, json, os, io
from PIL import Image

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
                                headers={"Content-Type": "application/json", "Authorization": "Bearer "+ os.environ['MISTRAL_TOKEN']},
                                json=data)
        response = json.loads(response.text)
        if response.get("choices", False):
            return response["choices"][0]["message"]["content"]
        else:
            return "Возникла ошибка"

    def free_gpt_4o_mini(self, prompt: str) -> tuple[str, int, int]|str:
        data = {
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.6,
            "top_p": 0.8,
            "max_tokens": 1024,
            "model": "gpt-4o-mini"
        }
        response = requests.post("https://models.inference.ai.azure.com/chat/completions",
                                headers={"Authorization": os.environ['GIT_TOKEN'], "Content-Type" : "application/json"},
                                json=data)
        if response.status_code == 200:
            response = json.loads(response.text)
            return response["choices"][0]["message"]["content"]
        return self._mistral_large_2407(prompt=prompt) 