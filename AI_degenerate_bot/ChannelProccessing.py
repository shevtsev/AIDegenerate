import logging, time
from md2tgmd import escape
from telebot import TeleBot
from Auxillary_class import keyboards
from neural_networks import neural_networks
from files.config import config

key = keyboards()
nn = neural_networks()
bot = TeleBot(config.token)
logger = logging.getLogger(__name__)

def request_processing(template: dict[str, str], prompt: str) -> None:
    text_prompt = template["text"] + prompt
    
    text = nn.free_gpt_4o_mini(text_prompt)
    text = text[:1020].rsplit(' ', 1)[0] + '...' if len(text) >= 1024 else text
    keyboard = key.keyboard_two_blank(['Опубликовать', 'Отклонить', 'Убрать изображение'], ['public', 'reject', 'img_del'])
    img = open("AI_degenerate_bot/files/empty_img.png", "rb")
    bot.send_photo(chat_id=config.private_chat_id, photo=img, caption=escape(text), reply_markup=keyboard, parse_mode='MarkdownV2')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'select':
        #С сайта
        if 'https://' in call.message.text:
            text = call.message.text
            request_processing(config.template['sites_prompt'], text)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.error(f"Error while deleting message: {e}")
        #С тг канала без картинки
        else:
            text = call.message.text
            request_processing(config.template['tg_prompt'], text)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                logger.error(f"Error while deleting message: {e}")

    if call.data == 'delete':
        try:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")
        
    #Кнопка опубликовать
    if call.data == 'public':
        if call.message.caption is not None:
            photo = bot.download_file(bot.get_file(call.message.photo[-1].file_id).file_path)
            bot.send_photo(chat_id=config.public_chat_id, photo=photo, caption=call.message.caption)
        else:
            bot.send_message(chat_id=config.public_chat_id, text=call.message.text)
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.delete_message(call.message.chat.id, call.message.message_id-1)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")

    #Кнопка отклонить
    elif call.data == 'reject':
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.delete_message(call.message.chat.id, call.message.message_id-1)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")

    elif call.data == 'img_del':
        bot.send_message(chat_id =call.message.chat.id, text=call.message.caption, reply_markup=key.keyboard_two_blank(['Опубликовать', 'Отклонить', 'Добавить изображение'], ['public', 'reject', 'img_add']), parse_mode='html')
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")
    
    elif call.data == 'img_add':
        bot.send_photo(chat_id =call.message.chat.id, photo=open("AI_degenerate_bot/files/empty_img.png", "rb"), caption=call.message.text, reply_markup=key.keyboard_two_blank(['Опубликовать', 'Отклонить', 'Добавить изображение'], ['public', 'reject', 'img_add']), parse_mode='html')
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            logger.error(f"Error while deleting message: {e}")

if __name__ == "__main__":
    while True:
        try:
            bot.polling()
        except Exception as e:
            logger.error(f"Polling exception {e}")
        time.sleep(2)