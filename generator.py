"""
Генератор лендинга Platinum Boost.
Генерирует карусель (8 случайных игр), таблицу всех игр,
JS-массив с данными, мета-теги и schema.org.
Поддерживает обновление счётчика платин и времени последнего обновления.
"""
import json
import os
import random
import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass

DATA_FILE = "data.json"
HTML_FILE = "index.html"
MAPPING_FILE = "mapping.json"
CAROUSEL_COUNT = 8
SITE_URL = "https://safeboostpsn-debug.github.io/platinum-boost"

@dataclass
class GameImages:
    cover: Optional[str] = None
    icon: Optional[str] = None

def load_platinums() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        print(f"{DATA_FILE} не найден.")
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_mapping() -> Dict[str, GameImages]:
    if not os.path.exists(MAPPING_FILE):
        print(f"{MAPPING_FILE} не найден.")
        return {}
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for item in data.get("mappings", []):
        game = item["game"].strip().lower()
        cover = item.get("cover", "")
        icon = item.get("icon", "")
        if cover and not os.path.exists(cover):
            cover = ""
        if icon and not os.path.exists(icon):
            icon = ""
        mapping[game] = GameImages(cover=cover or None, icon=icon or None)
    print(f"Загружено маппингов: {len(mapping)}")
    return mapping

def generate_slides(platinums: List[dict], mapping: Dict[str, GameImages]) -> str:
    """Генерирует HTML для 8 слайдов карусели."""
    lines = []
    for p in platinums:
        game_key = p["name"].strip().lower()
        imgs = mapping.get(game_key, GameImages())
        cover = p.get("cover", "") or imgs.cover or ""
        icon = imgs.icon or ""

        if cover and os.path.exists(cover):
            cover_html = f'<img src="{cover}" class="cover-img" alt="{p["name"]}">'
        else:
            letter = p["name"][0].upper() if p["name"] else "?"
            cover_html = f'<div class="cover-img" style="background:linear-gradient(135deg,{p.get("color","#3b82f6")}, {p.get("color","#3b82f6")}dd);display:flex;align-items:center;justify-content:center;font-size:80px;font-weight:700;color:rgba(255,255,255,0.25);">{letter}</div>'

        # Значок платины
        icon_html = f'<img src="{icon}" style="width:32px;height:32px;" alt="🏆">' if icon else ''
        plat_badge = f'<div class="plat-badge">{icon_html}<span>Платина</span></div>' if icon else '<div class="plat-badge"><span>🏆 Платина</span></div>'

        # Текст для шеринга
        share_text = f"Платина%20в%20{p['name'].replace(' ', '%20')}%20–%20{p['trophies']}%20трофеев%20за%20{p['time'].replace(' ', '%20')}"
        share_url = f"https://t.me/share/url?url={SITE_URL}&text={share_text}"

        lines.append(f'''        <div class="carousel-slide" data-game="{p["name"]}" data-platform="{p["platform"]}" data-trophies="{p["trophies"]}" data-time="{p["time"]}" data-difficulty="{p["difficulty"]}" data-color="{p.get("color","#3b82f6")}">
            {cover_html}
            <div class="info-overlay">
                {plat_badge}
                <div class="game-name">{p["name"]} ({p["platform"]})</div>
                <div class="game-stats">
                    <div class="stat-item"><div class="stat-value">{p["trophies"]}</div><div class="stat-label">трофеев</div></div>
                    <div class="stat-item"><div class="stat-value">{p["time"]}</div><div class="stat-label">время</div></div>
                    <div class="stat-item"><div class="stat-value">{p["difficulty"]}</div><div class="stat-label">сложность</div></div>
                </div>
                <a class="share-btn" href="{share_url}" target="_blank" title="Поделиться в Telegram">
                    <img src="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2394a3b8'%3E%3Cpath d='M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.05-.2-.07-.06-.17-.04-.25-.02-.11.02-1.84 1.17-5.2 3.44-.49.34-.94.5-1.34.49-.44-.01-1.28-.25-1.9-.45-.77-.25-1.38-.38-1.33-.81.03-.22.34-.45.94-.68 3.7-1.61 6.17-2.68 7.4-3.19 3.52-1.46 4.25-1.72 4.73-1.73.1 0 .33.02.48.14.12.09.16.22.18.31.02.1.04.33.02.5z'/%3E%3C/svg%3E" alt="Share"> Поделиться
                </a>
            </div>
        </div>''')
    return "\n".join(lines)

def generate_table(platinums: List[dict]) -> str:
    """Генерирует HTML-таблицу со всеми играми (вставляется в модалку)."""
    rows = []
    for p in platinums:
        rows.append(f'''                    <tr>
                        <td>{p["name"]}</td>
                        <td>{p["platform"]}</td>
                        <td>{p["trophies"]}</td>
                        <td>{p["time"]}</td>
                        <td>{p["difficulty"]}</td>
                    </tr>''')
    return f'''<table class="all-plat-table" id="fullPlatTable">
                <thead>
                    <tr>
                        <th>Игра</th>
                        <th>Платформа</th>
                        <th>Трофеи</th>
                        <th>Время</th>
                        <th>Сложность</th>
                    </tr>
                </thead>
                <tbody>
{chr(10).join(rows)}
                </tbody>
            </table>'''

def generate_js_data(platinums: List[dict]) -> str:
    """Генерирует JavaScript-массив со всеми играми для фильтрации и поиска."""
    games_for_js = []
    for p in platinums:
        games_for_js.append({
            "name": p["name"],
            "platform": p["platform"],
            "trophies": p["trophies"],
            "time": p["time"],
            "difficulty": p["difficulty"],
            "color": p.get("color", "#3b82f6"),
            "cover": p.get("cover", "")
        })
    return f'<script>window.allPlatinums = {json.dumps(games_for_js, ensure_ascii=False)};</script>'

def generate_meta_tags(total: int, last_name: str, last_time: str) -> str:
    """Генерирует мета-теги и schema.org."""
    now_utc = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    description = f"Выбиваю платиновые трофеи на PS4/PS5 вручную. Уже {total} платин. Без читов, официальный шейринг. От 1500₽."
    return f'''    <!-- Primary Meta Tags -->
    <meta name="description" content="{description}">
    <meta name="keywords" content="платина, трофеи, PS4, PS5, помощь с трофеями, boost, platinum">
    <meta name="author" content="Platinum Boost">
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}">
    <meta property="og:title" content="Platinum Boost — платины PS4/PS5 под ключ">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{SITE_URL}/preview.jpg">
    <!-- Twitter -->
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{SITE_URL}">
    <meta property="twitter:title" content="Platinum Boost — платины PS4/PS5">
    <meta property="twitter:description" content="{description}">
    <meta property="twitter:image" content="{SITE_URL}/preview.jpg">
    <!-- Schema.org -->
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "Service",
      "name": "Platinum Boost",
      "description": "{description}",
      "provider": {{ "@type": "Person", "name": "Platinum Booster" }},
      "priceRange": "₽1500 - ₽10000",
      "areaServed": "Worldwide",
      "aggregateRating": {{
        "@type": "AggregateRating",
        "ratingValue": "5.0",
        "reviewCount": "25"
      }},
      "serviceOutput": {{
        "@type": "Game",
        "name": "Platinum trophy"
      }}
    }}
    </script>'''

def update_html(platinums: List[dict], mapping: Dict[str, GameImages]) -> None:
    """Основная функция: читает шаблон index.html, вставляет сгенерированные блоки."""
    if not os.path.exists(HTML_FILE):
        print(f"Шаблон {HTML_FILE} не найден!")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Выбираем 8 случайных игр для карусели
    carousel_plats = random.sample(platinums, min(CAROUSEL_COUNT, len(platinums)))
    slides_html = generate_slides(carousel_plats, mapping)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ СЛАЙДЫ ЗДЕСЬ -->', slides_html)

    # 2. Таблица всех игр (вставляется в модалку)
    table_html = generate_table(platinums)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ ТАБЛИЦУ ЗДЕСЬ -->', table_html)

    # 3. JS-массив всех игр
    js_data = generate_js_data(platinums)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ JS ДАННЫЕ -->', js_data)

    # 4. Обновляем счётчик платин, последнюю платину и время обновления
    total = len(platinums)
    last_game = platinums[0]  # предполагаем, что первая игра в списке — самая последняя
    last_name = last_game["name"]
    last_time = last_game["time"]
    now_utc = datetime.utcnow().strftime('%d.%m.%Y, %H:%M UTC')

    html = re.sub(r'Уже \d+ платин', f'Уже {total} платин', html)
    html = re.sub(r'<strong id="lastPlatName">.*?</strong>', f'<strong id="lastPlatName">{last_name}</strong>', html)
    html = re.sub(r'<span id="lastPlatTime">.*?</span>', f'<span id="lastPlatTime">{last_time}</span>', html)
    html = re.sub(r'<span id="lastUpdate">.*?</span>', f'<span id="lastUpdate">{now_utc}</span>', html)

    # 5. Мета-теги
    meta_tags = generate_meta_tags(total, last_name, last_time)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ МЕТА-ТЕГИ -->', meta_tags)

    # 6. (Опционально) можно минимифицировать HTML, удалив лишние пробелы
    # Но пока оставим как есть.

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html обновлён. Всего платин: {total}, карусель: {len(carousel_plats)} игр.")

def main():
    platinums = load_platinums()
    if not platinums:
        print("Нет данных в data.json, выход.")
        return
    mapping = load_mapping()
    update_html(platinums, mapping)
    print("Готово.")

if __name__ == "__main__":
    main()
