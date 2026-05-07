"""
Скачивает обложки игр из PS Store API и сохраняет в папку covers/.
Запустить один раз вручную или через Actions.
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
    """Ищет обложку игры в PS Store. Возвращает URL или None."""
    try:
        short_name = game_name.split(":")[0].split(" - ")[0].strip()
        query = urllib.parse.quote(short_name)
        url = f"{PS_STORE_API}{query}"
        print(f"  Ищу: {short_name} -> {url}")
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://store.playstation.com/"}, timeout=15)
        data = r.json()
        if "links" in data and data["links"]:
            for item in data["links"]:
                if "images" in item:
                    for img in item["images"]:
                        if img["type"] == 10:  # type=10 — полноценная обложка
                            print(f"    Найдена обложка type=10: {img['url'][:80]}...")
                            return img["url"]
                        if img["type"] == 1:  # type=1 — иконка
                            print(f"    Найдена иконка type=1: {img['url'][:80]}...")
                            return img["url"]
    except Exception as e:
        print(f"    Ошибка: {e}")
    return None

def download_cover(game_name, cover_url):
    """Скачивает обложку и сохраняет в covers/."""
    try:
        safe_name = re.sub(r'[^a-z0-9]', '_', game_name.lower())[:30]
        ext = cover_url.split('.')[-1].split('?')[0]
        if ext not in ('png', 'jpg', 'jpeg'):
            ext = 'png'
        filename = f"{safe_name}_cover.{ext}"
        filepath = os.path.join(COVERS_DIR, filename)
        
        if os.path.exists(filepath):
            print(f"    Уже скачана: {filename}")
            return f"covers/{filename}"
        
        r = requests.get(cover_url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://store.playstation.com/"}, timeout=15)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f"    Сохранена: {filename} ({len(r.content)} байт)")
            return f"covers/{filename}"
    except Exception as e:
        print(f"    Ошибка скачивания: {e}")
    return None

def main():
    os.makedirs(COVERS_DIR, exist_ok=True)
    
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        platinums = json.load(f)
    
    print(f"Игр для скачивания: {len(platinums)}")
    
    for p in platinums:
        name = p["name"]
        print(f"\n{name}")
        cover_url = search_cover(name)
        if cover_url:
            path = download_cover(name, cover_url)
            if path:
                p["cover"] = path
        else:
            print(f"    Обложка не найдена")
    
    # Сохраняем обновлённый data.json
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(platinums, f, ensure_ascii=False, indent=2)
    print(f"\nГотово. Обновлён {DATA_FILE}")

if __name__ == "__main__":
    main()
