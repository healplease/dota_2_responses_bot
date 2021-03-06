from flask import Blueprint, request, abort
import telebot

from app import bot
from config import Config

main_bp = Blueprint("bot", __name__)

@main_bp.route(f"/{Config.TELEGRAM_API_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_string)
        bot.bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)
