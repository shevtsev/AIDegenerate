import requests, asyncio, logging
from telebot import TeleBot
from telethon import TelegramClient, events
from bs4 import BeautifulSoup
from Auxillary_class import keyboards
from neural_networks import neural_networks
from files.config import config

key = keyboards()
logger = logging.getLogger(__name__)

# Класс со всеми парсерами
class Parsers(neural_networks):
    def __init__(self):
        self.__bot = TeleBot(token=config.token)
        self.__chat_id = config.chat_id

# Private
    # Получение ссылки и заголовки новости
    def __site_parse_method(self, news: str, link: list[str]) -> str:
        try:
            response = requests.get(news)
            soup = BeautifulSoup(response.content, 'html.parser')
            el = soup.find(link[0], class_=link[1])
            href = el['href']
            if "https://" in href:
                return href
            elif link[2] != "":
                return link[2] + href
            return news+href
        except Exception as e:
            logger.error(f"Error in site_parse_method: {e}")

#Public
    #Парсер для тг каналов
    def telegram_parser(self, loop=None) -> TelegramClient:
        client = TelegramClient('session', config.api_id, config.api_hash, loop=loop)
        client.start()

        @client.on(events.NewMessage())
        async def handler(event):
            channels = list(config.urls['channels'])

            chat = await client.get_entity(event.message.peer_id)
            if f"@{chat.username}" in channels:
                self.__bot.send_message(chat_id=self.__chat_id, text=str(event.raw_text), reply_markup=key.keyboard_two_blank(['Выбрать', 'Удалить'], ['select', 'delete']))
        return client
    
    #Парсер для сайтов
    async def SitesParse(self, urls: dict[str, list[str|bool]]):
        #Последние опубликованные новости
        last_news = {news: [self.__site_parse_method(news=news, link=link)] for news, link in urls.items()}
        logger.info(f"News dict: {last_news}")
        #Цикл обработки новой новости
        while True:
            for news, link in urls.items():
                href = self.__site_parse_method(news=news, link=link)
                if href is not None and href not in last_news[news]:
                    self.__bot.send_message(chat_id=self.__chat_id, text=href, reply_markup=key.keyboard_two_blank(['Выбрать', 'Удалить'], ['select', 'delete']), parse_mode='html')
                    if len(last_news[news]) >= 5:
                        last_news[news].pop(0)
                    last_news[news].append(href)
                    logging.info(f"Added news: {href}, new list of news: {last_news}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    urls = config.urls['urls']
    parse = Parsers()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = parse.telegram_parser(loop=loop)
    loop.create_task(parse.SitesParse(urls=urls))
    client.run_until_disconnected()