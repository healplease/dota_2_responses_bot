from urllib.parse import urlencode

from flask import Flask
from flask_mongoengine import MongoEngine

from app.bot import TelegramBot
from config import environment_configs

bot = TelegramBot()
mongoengine = MongoEngine()


def create_app():
    app = Flask(__name__)
    app.config.from_object(f"config.{environment_configs[app.env].__name__}")

    mongodb_settings = app.config.get_namespace("MONGODB_")
    mongodb_settings["port"] = f":{mongodb_settings.get('port')}" if mongodb_settings.get("port") else ""
    mongodb_settings["arguments"] = (
        f"?{urlencode(mongodb_settings.get('arguments'))}" if mongodb_settings.get("arguments") else ""
    )
    app.config["MONGODB_HOST"] = "{protocol}://{username}:{password}@{host}{port}/{db}{arguments}".format(
        **mongodb_settings
    )

    mongoengine.init_app(app)

    from app.views import main_bp
    app.register_blueprint(main_bp)

    bot.init_app(app)

    return app
