import requests, asyncio, json, os
from telebot import TeleBot
from dotenv import load_dotenv
from telethon import TelegramClient, events
from bs4 import BeautifulSoup
from Auxillary_class import keyboards
from neural_networks import neural_networks

load_dotenv()
key = keyboards()
#Класс со всеми парсерами
class Parsers(neural_networks):
    def __init__(self):
        self.__bot = TeleBot(token=os.environ['TOKEN'])
        self.__chat_id = -1002376640623

#Private
    #Получение ссылки и заголовки новости
    def __site_parse_method(self, news: str, link: list[str]) -> str:
        response = requests.get(news)
        soup = BeautifulSoup(response.content, 'html.parser')
        el = soup.find(link[0], class_=link[1])
        href = el['href']
        if "https://" in href:
            return href
        elif link[2] != "":
            return link[2] + href
        return news+href

#Public
    #Парсер для тг каналов
    def telegram_parser(self, loop=None) -> TelegramClient:
        api_id = os.environ['API_ID']
        api_hash = os.environ['API_HASH']
        client = TelegramClient('session', api_id, api_hash, loop=loop)
        client.start()

        @client.on(events.NewMessage())
        async def handler(event):
            with open("AI_degenerate_bot/files/urls.json", 'r') as file:
                channels = list(json.load(file)['channels'])

            chat = await client.get_entity(event.message.peer_id)
            if f"@{chat.username}" in channels:
                self.__bot.send_message(chat_id=self.__chat_id, text=str(event.raw_text), reply_markup=key.keyboard_two_blank(['Выбрать', 'Удалить'], ['select', 'delete']))
        return client
    
    #Парсер для сайтов
    async def SitesParse(self, urls: dict[str, list[str|bool]]):
        #Последние опубликованные новости
        last_news = {news: self.__site_parse_method(news=news, link=link) for news, link in urls.items()}

        #Цикл обработки новой новости
        while True:
            for news, link in urls.items():
                href = self.__site_parse_method(news=news, link=link)
                if href != last_news[news]:
                    print(last_news)
                    self.__bot.send_message(chat_id=self.__chat_id, text=href, reply_markup=key.keyboard_two_blank(['Выбрать', 'Удалить'], ['select', 'delete']), parse_mode='html')
                    last_news[news] = href
            await asyncio.sleep(5)

if __name__ == "__main__":
    with open("AI_degenerate_bot/files/urls.json", 'r') as file:
        urls = json.load(file)['urls']
    parse = Parsers()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    client = parse.telegram_parser(loop=loop)
    loop.create_task(parse.SitesParse(urls=urls))
    client.run_until_disconnected()