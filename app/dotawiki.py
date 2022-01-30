import json
import os
import random
import re
import string
import time
from urllib.parse import urljoin

import bs4
import requests

from app.models import Hero, HeroResponse


class DotaWikiScrapper:
    def __init__(self, from_cache=True):
        self.base_url = "https://dota2.fandom.com"
        self.cache = ".cache.json"
        if os.path.exists(self.cache) and from_cache:
            print("dotawiki - Loading responses from cache")
            with open(self.cache, "r", encoding="utf-8") as cached:
                self.responses = json.load(cached)
        else:
            print("dotawiki - Loading responses from web")
            self.responses = { 
                hero_id: {"name": name, "responses": self.fetch_hero_response_sounds(hero_id)}
                for hero_id, name
                in self.fetch_heroes_list().items()
            }
            with open(self.cache, "w", encoding="utf-8") as cached:
                json.dump(self.responses, cached)
        print(f"dotawiki - Loaded {len(tuple(self.responses.keys()))} heroes' responses.")
        if not [hero.name for hero in Hero.objects().all()]:
            self.populate_db()

    def populate_db(self):
        answer = input("This function is about to drop all documents in DB. Do you want to proceed? (y/n): ")
        if answer != "y":
            return None
        heroes_deleted = Hero.objects().delete()
        print(f"Cleared Hero model objects - {heroes_deleted} objects deleted.")
        responses_deleted = HeroResponse.objects().delete()
        print(f"Cleared HeroResponse model objects - {responses_deleted} objects deleted.")

        for hero_id, hero_data in self.responses.items():
            Hero.objects.create(name=hero_data["name"], url_name=hero_id)
            for url, text in hero_data["responses"].items():
                HeroResponse.objects.create(text=text, url=url, hero=Hero.objects(name=hero_data["name"]).first())
            print(f"Inserted {len(list(hero_data['responses'].keys()))} responses of {hero_data['name']} to DB.")
        print(f"Inserted {len(list(self.responses.keys()))} heroes to DB.")

    def fetch_heroes_list(self):
        print("dotawiki - Fetching heroes list...")
        response = requests.get(urljoin(self.base_url, "wiki/Heroes"))
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        heroes_elements = soup.select("div.mw-parser-output td a")
        heroes = {
            element["href"].replace("/wiki/", ""): element["title"]
            for element
            in heroes_elements
        }
        print(f"dotawiki - Fetched {len(heroes)} heroes.")
        return heroes

    def fetch_hero_response_sounds(self, hero: str):
        print(f"dotawiki - Fetching {hero}'s responses...")
        response = requests.get(urljoin(self.base_url, f"wiki/{hero}/Responses"))
        soup = bs4.BeautifulSoup(response.text, features="html.parser")
        responses_elements = soup.select(".mw-parser-output ul li")

        def sanitize_response(el: bs4.PageElement) -> str:
            return el.find(text=True, recursive=False)

        responses = {}
        
        for response in responses_elements:
            response = str(response).replace("</a>", "")
            link = re.search(r"https:\/\/.+?\.mp3", response)
            text = re.search(r"[^>]*?</li>", response)
            if link and text:
                link = link.group(0)
                text = text.group(0).replace("</li>", "").strip()
                responses[link] = text

        print(f"dotawiki - Fetched {len(tuple(responses.keys()))} of {hero}'s responses...")
        return responses

    def pick_random_hero_response(self, query: str, strict: bool=True, multi: bool=False):
        if strict:
            responses = HeroResponse.objects(text__iexact=query)
        else:
            t = time.perf_counter()
            responses = HeroResponse.objects.search_text(query).order_by('$text_score').limit(50)
            print(f"search done in {time.perf_counter() - t}, {len(responses)} found")
        if not multi:
            response = responses.first()
            if not response:
                result = None
            else:
                result = {
                    "response": response.text,
                    "url": response.url,
                    "name": response.hero.name
                }
        else:
            result = []
            for response in responses:
                result.append(
                    {
                    "response": response.text,
                    "url": response.url,
                    "name": response.hero.name
                    }
                )
            print(f"Found {len(result)} responses for query '{query}'")
        return result

if __name__ == "__main__":
    scrapper = DotaWikiScrapper()
