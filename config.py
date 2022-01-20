import os


class Config():
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SERVER_NAME = os.environ.get("FLASK_SERVER_NAME")
    SERVER_NAME = os.environ.get("SERVER_NAME")
    TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")


class LocalConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


environment_configs = {
    "local": LocalConfig,
    "production": ProductionConfig
}
