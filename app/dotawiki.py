import json
import os
import random
import string
from urllib.parse import urljoin

import bs4
import requests


class DotaWikiScrapper:
    def __init__(self, from_cache=True):
        self.base_url = "https://dota2.fandom.com"
        self.cache = ".cache.json"
        if os.path.exists(self.cache) and from_cache:
            print("dotawiki - Loading responses from cache")
            with open(self.cache, "r", encoding="utf-8") as cached:
                self.responses = json.load(cached)
            print(f"dotawiki - Loaded {len(tuple(self.responses.keys()))} heroes' responses.")
        else:
            print("dotawiki - Loading responses from web")
            self.responses = { 
                hero_id: {"name": name, "responses": self.fetch_hero_response_sounds(hero_id)}
                for hero_id, name
                in self.fetch_heroes_list().items()
            }
            with open(self.cache, "w", encoding="utf-8") as cached:
                self.responses = json.dump(self.responses, cached)


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

        responses = {
            element.text.replace("Link▶️", "").strip(): element.select_one("source")["src"].split("?")[0]
            for element
            in responses_elements
            if (sanitize_response(element) and element.select("source") and not element.select("small span"))
        }
        print(f"dotawiki - Fetched {len(tuple(responses.keys()))} of {hero}'s responses...")
        return responses

    def pick_random_hero_response(self, response: str, strict: bool=True, multi: bool=False):
        multi_list = []
        response_stripped = response.lower()
        for item in string.punctuation:
            response_stripped = response_stripped.replace(item, "")
        heroes_list = list(self.responses.keys())
        random.shuffle(heroes_list)
        for hero_id in heroes_list:
            keys = list(self.responses[hero_id]["responses"].keys())
            for key in keys:
                key_stripped = key.lower()
                for item in string.punctuation:
                    key_stripped = key_stripped.replace(item, "")
                rule = response_stripped == key_stripped if strict else response_stripped in key_stripped
                if rule:
                    print(f"dotawiki - Found response '{key}' of {self.responses[hero_id]['name']}")
                    hero_response = {
                        "response": key,
                        "url": self.responses[hero_id]["responses"][key],
                        "name": self.responses[hero_id]["name"]
                    }
                    if not multi:
                        return hero_response
                    else:
                        multi_list.append(hero_response)
        if not multi:
            print(f"dotawiki - No hero response found for '{response}'.")
            return None
        else:
            print(f"dotawiki - Found {len(multi_list)} responses for '{response}'.")
            return multi_list

if __name__ == "__main__":
    scrapper = DotaWikiScrapper()
    print(scrapper.pick_random_hero_response("who calls", strict=False, multi=True))
