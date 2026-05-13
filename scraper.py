"""
Сбор платин с PSNProfiles через Selenium + Chrome.
"""
import re
import hashlib
import json
import time
from dataclasses import dataclass, asdict
from typing import List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

PSN_URL = "https://psnprofiles.com/SASHOK911"
DATA_FILE = "data.json"
MAX_PLATINUMS = 40

@dataclass
class Platinum:
    name: str
    platform: str
    trophies: str
    difficulty: str
    time: str
    color: str = ""

    def __post_init__(self):
        if not self.color:
            self.color = "#" + hashlib.md5(self.name.encode()).hexdigest()[:6]

def fetch_platinums() -> List[Platinum]:
    print(f"Запрашиваю {PSN_URL}...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(PSN_URL)
        time.sleep(10)
        # PSNProfiles использует другую структуру — ищем все игры с платиной
        rows = driver.find_elements(By.CSS_SELECTOR, "table tr, .game-list-item, .game")
        print(f"Найдено элементов: {len(rows)}")

        platinums = []
        for row in rows:
            try:
                text = row.text
                if "100%" not in text:
                    continue
                # Парсим имя игры (первая строка до разрыва)
                lines = text.split('\n')
                name = lines[0].strip() if lines else ""
                name = re.sub(r'\s*\(.*?\)\s*', '', name)
                if not name:
                    continue
                # Ищем платформу
                platform = "PS5" if "PS5" in text else "PS4"
                # Ищем трофеи (например "48 of 48")
                m = re.search(r'(\d+)\s*of\s*(\d+)', text) or re.search(r'(\d+)/(\d+)', text)
                if m and m.group(1) == m.group(2):
                    trophies = m.group(2)
                else:
                    continue
                platinums.append(Platinum(
                    name=name,
                    platform=platform,
                    trophies=trophies,
                    difficulty="?",
                    time="?"
                ))
            except:
                continue

        print(f"Собрано платин: {len(platinums)}")
        return platinums[:MAX_PLATINUMS]
    finally:
        driver.quit()

def main():
    platinums = fetch_platinums()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in platinums], f, ensure_ascii=False, indent=2)
    print(f"Сохранено в {DATA_FILE}")

if __name__ == "__main__":
    main()
