import io
import random
import re
import string
from multiprocessing import Process, Manager

from flask import Flask, url_for
from mutagen.mp3 import MPEGInfo
import requests
import telebot

from app.dotawiki import DotaWikiScrapper

def telegram_audio_result(response: dict, answer_id: int, results: list):
    text = f"<a href='{response['url']}'><b>{response['response']}</b></a> - <i>{response['name']}</i>"
    audio_response = requests.get(response["url"])
    input_audio_message = telebot.types.InputMediaAudio(
        media=io.BytesIO(audio_response.content),
        caption=text,
        parse_mode="HTML",
        duration=MPEGInfo(io.BytesIO(audio_response.content)).length,
        performer=response["name"],
        title=response["response"]
    )
    inline_query_preview = telebot.types.InlineQueryResultAudio(
        id=answer_id,
        audio_url=response["url"],
        title=response['response'],
        caption=text,
        parse_mode="HTML",
        performer=response["name"],
        audio_duration=int(MPEGInfo(io.BytesIO(audio_response.content)).length) + 1,
        input_message_content=input_audio_message
    )
    results.append(inline_query_preview)
    return inline_query_preview



class TelegramBot:
    def __init__(self, app: Flask=None):
        self.bot: telebot.TeleBot = None
        telebot.logger.setLevel(telebot.logging.WARNING)
        if app:
            self.init_app(app)
        

    def init_app(self, app: Flask):
        self.scrapper = DotaWikiScrapper()
        self.bot = telebot.TeleBot(app.config["TELEGRAM_API_TOKEN"])

        @self.bot.message_handler(content_types=["text"])
        def dota_response_handler(message: telebot.types.Message):
            pattern = re.compile("[a-zA-Z0-9_ " + string.punctuation + "]")
            if re.match(pattern, message.text):
                responses = self.scrapper.pick_random_hero_response(message.text, strict=True, multi=True)
                if responses:
                    response = random.choice(self.scrapper.pick_random_hero_response(message.text, strict=True, multi=True))
                    text = f"<a href='{response['url']}'><b>{response['response']}</b></a> - <i>{response['name']}</i>"
                    audio_response = requests.get(response["url"])
                    self.bot.send_audio(
                        chat_id=message.chat.id,
                        audio=io.BytesIO(audio_response.content), 
                        caption=text,
                        parse_mode="HTML",
                        reply_to_message_id=message.id,
                        duration=MPEGInfo(io.BytesIO(audio_response.content)).length,
                        title=response["response"],
                        performer=response["name"],
                    )


        @self.bot.inline_handler(lambda x: len(x.query) > 2)
        def dota_inline_response_handler(inline_query: telebot.types.InlineQuery):
            responses = self.scrapper.pick_random_hero_response(query=inline_query.query, strict=False, multi=True)
            results = Manager().list()
            task_list = []
            for response in responses:
                task = Process(target=telegram_audio_result)
                task_list.append(task)
                task._args = (response, len(task_list), results)
                task.start()
            for task in task_list:
                task.join()

            self.bot.answer_inline_query(inline_query.id, results)


        self.bot.remove_webhook()
        if not app.config["SERVER_NAME"] == "0.0.0.0":
            self.bot.set_webhook("https://" + app.config["SERVER_NAME"] + f"/{app.config['TELEGRAM_API_TOKEN']}")
        else:
            self.bot.infinity_polling()
        return self.bot
