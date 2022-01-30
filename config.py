import os


class Config():
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    SERVER_NAME = os.environ.get("FLASK_SERVER_NAME")
    SERVER_NAME = os.environ.get("SERVER_NAME")
    TELEGRAM_API_TOKEN = os.environ.get("TELEGRAM_API_TOKEN")

    MONGODB_USERNAME = os.environ.get("FLASK_MONGODB_USER")
    MONGODB_PASSWORD = os.environ.get("FLASK_MONGODB_PASSWORD")
    MONGODB_HOST = os.environ.get("FLASK_MONGODB_HOST")
    MONGODB_PORT = os.environ.get("FLASK_MONGODB_PORT")
    MONGODB_DB = "dota_responses_bot"
    MONGODB_PROTOCOL = "mongodb+srv"
    MONGODB_ARGUMENTS = {"retryWrites": "true", "w": "majority"}


class LocalConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    pass


environment_configs = {
    "local": LocalConfig,
    "production": ProductionConfig
}
