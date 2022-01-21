from flask import Blueprint, request, abort

from config import Config

main_bp = Blueprint("bot", __name__)

@main_bp.route(f"/{Config.TELEGRAM_API_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data(as_text=True)
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return '', 200
    else:
        abort(403)
