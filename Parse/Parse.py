import requests, asyncio, logging
from telebot import TeleBot
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from bs4 import BeautifulSoup
from Auxillary_class import keyboards
from neural_networks import neural_networks
from files.config import config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

key = keyboards()

# Класс со всеми парсерами
class Parsers(neural_networks):
    def __init__(self):
        self.__bot = TeleBot(token=config.token)
        self.__chat_id = config.chat_id

# Private
    # Получение ссылки и заголовки новости
    def __site_parse_method(self, news: str, link: list[str]) -> str:
        try:
            logger.info(f"Attempting to parse {news}")
            response = requests.get(news)
            logger.debug(f"Got response from {news} with status code: {response.status_code}")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            el = soup.find(link[0], class_=link[1])
            
            if el is None:
                logger.warning(f"Could not find element with tag {link[0]} and class {link[1]} on {news}")
                return None
                
            href = el['href']
            logger.debug(f"Found href: {href}")
            
            if "https://" in href:
                logger.debug("URL is absolute, returning as is")
                return href
            elif link[2] != "":
                full_url = link[2] + href
                logger.debug(f"URL is relative, constructed full URL: {full_url}")
                return full_url
            
            full_url = news + href
            logger.debug(f"URL is relative, constructed full URL: {full_url}")
            return full_url
            
        except Exception as e:
            logger.error(f"Error parsing {news}: {str(e)}", exc_info=True)
            return None

#Public
    #Парсер для тг каналов
    def telegram_parser(self, loop=None) -> TelegramClient:
        try:
            logger.info("Initializing Telegram client...")
            client = TelegramClient(StringSession(open("session.txt").readline()), config.api_id, config.api_hash, loop=loop)
            
            logger.info("Starting Telegram client...")
            client.start()
            logger.info("Telegram client started successfully")

            @client.on(events.NewMessage())
            async def handler(event):
                try:
                    channels = list(config.urls['channels'])
                    chat = await client.get_entity(event.message.peer_id)
                    
                    logger.info(f"Received message from {chat.username}")
                    
                    if f"@{chat.username}" in channels:
                        logger.info(f"Processing message from channel {chat.username}")
                        self.__bot.send_message(
                            chat_id=self.__chat_id, 
                            text=str(event.raw_text), 
                            reply_markup=key.keyboard_two_blank(['Выбрать', 'Удалить'], ['select', 'delete'])
                        )
                except Exception as e:
                    logger.error(f"Error in message handler: {e}", exc_info=True)

            # Явный запуск цикла событий
            logger.info("Running event loop...")
            client.run_until_disconnected()
            
            return client
        except Exception as e:
            logger.error(f"Error in telegram_parser: {e}", exc_info=True)
            raise
    
    #Парсер для сайтов
    async def SitesParse(self, urls: dict[str, list[str|bool]]):
        logger.info("Starting website parser...")
        #Последние опубликованные новости
        last_news = {news: [self.__site_parse_method(news=news, link=link)] for news, link in urls.items()}
        logger.info(f"Initialized last news dictionary: {last_news}")
        
        #Цикл обработки новой новости
        logger.info("Starting news monitoring loop")
        while True:
            try:
                for news, link in urls.items():
                    logger.info(f"Checking website: {news}")
                    href = self.__site_parse_method(news=news, link=link)
                    
                    if href is None:
                        logger.warning(f"Failed to parse news from {news}")
                        continue
                        
                    if href not in last_news[news]:
                        logger.info(f"Found new article at {news}: {href}")
                        try:
                            self.__bot.send_message(
                                chat_id=self.__chat_id, 
                                text=href, 
                                reply_markup=key.keyboard_two_blank(['Выбрать', 'Удалить'], ['select', 'delete']), 
                                parse_mode='html'
                            )
                            logger.info(f"Successfully sent message to chat {self.__chat_id}")
                            
                            if len(last_news[news]) >= 5:
                                removed = last_news[news].pop(0)
                                logger.info(f"Removed oldest news from history: {removed}")
                                
                            last_news[news].append(href)
                            logger.info(f"Updated news history for {news}: {last_news[news]}")
                        except Exception as e:
                            logger.error(f"Error sending message to Telegram: {e}", exc_info=True)
                    else:
                        logger.debug(f"No new articles found at {news}")
                        
            except Exception as e:
                logger.error(f"Error in news monitoring loop: {e}", exc_info=True)
                
            logger.debug("Waiting 10 seconds before next check")
            await asyncio.sleep(10)

if __name__ == "__main__":
    urls = config.urls['urls']
    parse = Parsers()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = parse.telegram_parser(loop=loop)
    loop.create_task(parse.SitesParse(urls=urls))
    client.run_until_disconnected()