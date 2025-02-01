import logging
from dotenv import load_dotenv
from os import environ as env
from dataclasses import dataclass

@dataclass
class Config:
    __instance = None

    def __new__(cls):
      if cls.__instance is None:
        load_dotenv()
        logging.basicConfig(filename='out.log', level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        cls.__instance = super(Config, cls).__new__(cls)
        cls.__instance.chat_id = -1002376640623
        cls.__instance.public_chat_id = -1002307638261
        cls.__instance.private_chat_id = -1002376640623
        cls.__instance.token = env['TOKEN']
        cls.__instance.api_id = env['API_ID']
        cls.__instance.api_hash = env['API_HASH']
        cls.__instance.mistral_token = env['MISTRAL_TOKEN']
        cls.__instance.git_token = env['GIT_TOKEN']
        return cls.__instance
      
config = Config()