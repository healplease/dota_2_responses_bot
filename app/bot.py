import io
import random
import re
import string

from flask import Flask, url_for
from mutagen.mp3 import MPEGInfo
import requests
import telebot

from app.dotawiki import DotaWikiScrapper

scrapper = DotaWikiScrapper()


class TelegramBot:
    def __init__(self, app: Flask=None):
        self.bot: telebot.TeleBot = None
        telebot.logger.setLevel(telebot.logging.WARNING)
        if app:
            self.init_app(app)
        

    def init_app(self, app: Flask):
        self.bot = telebot.TeleBot(app.config["TELEGRAM_API_TOKEN"])

        @self.bot.message_handler(content_types=["text"])
        def dota_response_handler(message: telebot.types.Message):
            pattern = re.compile("[a-zA-Z0-9_ " + string.punctuation + "]")
            if re.match(pattern, message.text):
                responses = scrapper.pick_random_hero_response(message.text, strict=True, multi=True)
                if responses:
                    response = random.choice(scrapper.pick_random_hero_response(message.text, strict=True, multi=True))
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
            responses = scrapper.pick_random_hero_response(inline_query.query, strict=False, multi=True)
            results = []
            for response in responses:
                text = f"<a href='{response['url']}'><b>{response['response']}</b></a> - <i>{response['name']}</i>"
                audio_response = requests.get(response["url"])
                results.append(
                    telebot.types.InlineQueryResultAudio(
                        id=len(results) + 1,
                        audio_url=response["url"],
                        title=response['response'],
                        caption=text,
                        parse_mode="HTML",
                        performer=response["name"],
                        audio_duration=int(MPEGInfo(io.BytesIO(audio_response.content)).length) + 1,
                        input_message_content=telebot.types.InputMediaAudio(
                            media=io.BytesIO(audio_response.content),
                            caption=text,
                            parse_mode="HTML",
                            duration=MPEGInfo(io.BytesIO(audio_response.content)).length,
                            performer=response["name"],
                            title=response["response"]
                        )
                    )
                )
                if len(results) == 50:
                    break

            self.bot.answer_inline_query(inline_query.id, results)


        self.bot.remove_webhook()
        if not app.config["SERVER_NAME"] == "0.0.0.0":
            self.bot.set_webhook("https://" + app.config["SERVER_NAME"] + f"/{app.config['TELEGRAM_API_TOKEN']}")
        else:
            self.bot.infinity_polling()
        return self.bot
