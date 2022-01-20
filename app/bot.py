import string

from flask import Flask, url_for
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
            response = scrapper.pick_random_hero_response(message.text)
            if response:
                text = f"<a href='{response['url']}'><b>{response['response']}</b></a> - <i>{response['name']}</i>"
                self.bot.reply_to(message, text, parse_mode="HTML")

        self.bot.remove_webhook()
        if not app.config["SERVER_NAME"] == "0.0.0.0":
            self.bot.set_webhook("https://" + app.config["SERVER_NAME"] + f"/{app.config['TELEGRAM_API_TOKEN']}")
        else:
            self.bot.infinity_polling()
        return self.bot
