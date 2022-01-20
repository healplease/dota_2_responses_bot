from flask import Flask

from app.bot import TelegramBot
from config import environment_configs

bot = TelegramBot()


def create_app():
    app = Flask(__name__)
    app.config.from_object(f"config.{environment_configs[app.env].__name__}")

    from app.views import main_bp
    app.register_blueprint(main_bp)

    bot.init_app(app)

    return app
