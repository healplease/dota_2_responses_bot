from mongoengine import Document, StringField, URLField, ReferenceField

# from app import mongoengine as me


class Hero(Document):
    url_name = StringField()
    name = StringField()

    meta = { "indexes": [ { "fields": ["$name"] } ] }


class HeroResponse(Document):
    text = StringField()
    url = URLField()
    hero = ReferenceField(Hero)

    meta = { "indexes": [ { "fields": ["$text", "$hero"] } ] }
