"""
Скачивает обложки игр из PS Store API. Сохраняет в covers/, обновляет data.json.
"""
import requests
import urllib.parse
import os
import json
import re

PS_STORE_API = "https://store.playstation.com/store/api/chihiro/00_09_000/search/US/en/999/"
COVERS_DIR = "covers"
DATA_FILE = "data.json"

def search_cover(game_name):
    try:
        short_name = game_name.split(":")[0].split(" - ")[0].strip()
        query = urllib.parse.quote(short_name)
        url = f"{PS_STORE_API}{query}"
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://store.playstation.com/"}, timeout=15)
        data = r.json()
        if "links" in data and data["links"]:
            for item in data["links"]:
                if "images" in item:
                    for img in item["images"]:
                       
