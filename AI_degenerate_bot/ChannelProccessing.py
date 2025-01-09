import json
from md2tgmd import escape
from telebot import TeleBot
from dotenv import load_dotenv
from Auxillary_class import keyboards
from neural_networks import neural_networks
from os import environ

#Загрузка переменных окружения
load_dotenv()

key = keyboards()
nn = neural_networks()
bot = TeleBot(environ['TOKEN'])
public_chat_id = '-1002307638261'
private_chat_id = '-1002376640623'

def request_processing(template: dict[str, str], prompt: str, photo: bytes) -> None:
    text_prompt = template["text"] + prompt
        
    text = nn.free_gpt_4o_mini(text_prompt)
    text = text[:1020].rsplit(' ', 1)[0] + '...' if len(text) >= 1024 else text
    keyboard = key.keyboard_two_blank(['Опубликовать', 'Отклонить', 'Убрать изображение'], ['public', 'reject', 'img_del'])
    bot.send_photo(chat_id=private_chat_id, photo=photo, caption=escape(text), reply_markup=keyboard, parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'select':
        #Настройка шаблона промпта
        with open("AI_degenerate_bot/files/prompts.json", "r") as file:
            template = json.load(file)

        #Из тг канала с картинкой
        if call.message.caption is not None:
            text = call.message.caption
            photo = bot.download_file(bot.get_file(call.message.photo[-1].file_id).file_path)
            request_processing(template['tg_prompt'], text, photo)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        #С сайта
        elif 'https://' in call.message.text:
            text = call.message.text
            request_processing(template['sites_prompt'], text, open("AI_degenerate_bot/files/empty_img.png", "rb"))
            bot.delete_message(call.message.chat.id, call.message.message_id)
        #С тг канала без картинки
        else:
            text = call.message.text
            request_processing(template['tg_prompt'], text, open("AI_degenerate_bot/files/empty_img.png", "rb"))
            bot.delete_message(call.message.chat.id, call.message.message_id)

    if call.data == 'delete':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        
    #Кнопка опубликовать
    if call.data == 'public':
        if call.message.caption is not None:
            photo = bot.download_file(bot.get_file(call.message.photo[-1].file_id).file_path)
            bot.send_photo(chat_id=public_chat_id, photo=photo, caption=call.message.caption)
        else:
            bot.send_message(chat_id=public_chat_id, text=call.message.text)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id-1)

    #Кнопка отклонить
    elif call.data == 'reject':
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.delete_message(call.message.chat.id, call.message.message_id-1)

    elif call.data == 'img_del':
        bot.send_message(chat_id =call.message.chat.id, text=call.message.caption, reply_markup=key.keyboard_two_blank(['Опубликовать', 'Отклонить', 'Добавить изображение'], ['public', 'reject', 'img_add']), parse_mode='html')
        bot.delete_message(call.message.chat.id, call.message.message_id)
    
    elif call.data == 'img_add':
        bot.send_photo(chat_id =call.message.chat.id, photo=open("AI_degenerate_bot/files/empty_img.png", "rb"), caption=call.message.text, reply_markup=key.keyboard_two_blank(['Опубликовать', 'Отклонить', 'Добавить изображение'], ['public', 'reject', 'img_add']), parse_mode='html')
        bot.delete_message(call.message.chat.id, call.message.message_id)

if __name__ == "__main__":
    bot.infinity_polling(timeout=10, long_polling_timeout=5)