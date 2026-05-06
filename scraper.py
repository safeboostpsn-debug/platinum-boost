"""
Сбор платин со Stratege через Selenium + Chrome.
Запускается в GitHub Actions (7 ГБ RAM, предустановленный Chrome).
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

STRATEGE_URL = "https://stratege.ru/playstation/users/sana17/"
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
    print(f"Запрашиваю {STRATEGE_URL}...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=800,600")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get(STRATEGE_URL)
        time.sleep(10)
        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        print(f"Строк в таблице: {len(rows)}")
        platinums = []
        for row in rows:
            try:
                html = row.get_attribute("innerHTML") or ""
                if "platinum.png" not in html.lower():
                    continue
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) < 8:
                    continue
                name = cells[0].text.strip()
                name = re.sub(r'\s*\(.*?\)\s*', '', name)
                if not name or name in ("SASHOK911", "Доска платин", "Название", ""):
                    continue
                trophies_text = cells[3].text.strip() if len(cells) > 3 else "?"
                m = re.search(r'(\d+)/(\d+)', trophies_text)
                if not m or m.group(1) != m.group(2):
                    continue
                platinums.append(Platinum(
                    name=name,
                    platform=cells[2].text.strip() if len(cells) > 2 else "?",
                    trophies=m.group(2),
                    difficulty=cells[4].text.strip() if len(cells) > 4 else "?",
                    time=cells[10].text.strip() if len(cells) > 10 else "?"
                ))
            except Exception as e:
                print(f"Ошибка парсинга строки: {e}")
                continue
        print(f"Собрано платин: {len(platinums)}")
        return platinums[:MAX_PLATINUMS]
    finally:
        driver.quit()

def main():
    platinums = fetch_platinums()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in platinums], f, ensure_ascii=False, indent=2)
    print(f"Данные сохранены в {DATA_FILE}")

if __name__ == "__main__":
    main()
