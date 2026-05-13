#!/usr/bin/env python3
"""
Platinum Boost Generator
Поддерживает доказательства (proofs) и числовые поля для калькулятора цены.
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
        print(f"❌ {DATA_FILE} не найден.")
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def load_mapping() -> Dict[str, GameImages]:
    if not os.path.exists(MAPPING_FILE):
        print(f"⚠️ {MAPPING_FILE} не найден, обложки из маппинга не будут использованы.")
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
    print(f"📦 Загружено маппингов: {len(mapping)}")
    return mapping

def generate_slides(platinums: List[dict], mapping: Dict[str, GameImages]) -> str:
    """Генерирует HTML для карусели (8 случайных игр)."""
    lines = []
    for p in platinums:
        game_key = p["name"].strip().lower()
        imgs = mapping.get(game_key, GameImages())
        cover = p.get("cover", "") or imgs.cover or ""
        icon = imgs.icon or ""

        # Обложка
        if cover and os.path.exists(cover):
            cover_html = f'<img src="{cover}" class="cover-img" alt="{p["name"]}">'
        else:
            letter = p["name"][0].upper() if p["name"] else "?"
            cover_html = f'<div class="cover-img" style="background:linear-gradient(135deg,{p.get("color","#3b82f6")}, {p.get("color","#3b82f6")}dd);display:flex;align-items:center;justify-content:center;font-size:80px;font-weight:700;color:rgba(255,255,255,0.25);">{letter}</div>'

        # Иконка платины (если есть)
        icon_html = f'<img src="{icon}" style="width:32px;height:32px;" alt="🏆">' if icon else ''
        plat_badge = f'<div class="plat-badge">{icon_html}<span>Платина</span></div>' if icon else '<div class="plat-badge"><span>🏆 Платина</span></div>'

        # Кнопка "Поделиться"
        share_text = f"Платина%20в%20{p['name'].replace(' ', '%20')}%20–%20{p['trophies']}%20трофеев%20за%20{p['time'].replace(' ', '%20')}"
        share_url = f"https://t.me/share/url?url={SITE_URL}&text={share_text}"

        # Кнопка "Доказательство" – если есть proofs
        proofs = p.get("proofs", [])
        proof_button = ""
        if proofs and len(proofs) > 0:
            proof_url = proofs[0]  # показываем первый скриншот
            proof_button = f'''
            <a class="proof-btn" href="{proof_url}" target="_blank" title="Скриншот трофея">
                📸 Доказательство
            </a>
            '''

        lines.append(f'''
        <div class="carousel-slide" data-game="{p["name"]}" data-platform="{p["platform"]}" data-trophies="{p["trophies"]}" data-time="{p["time"]}" data-difficulty="{p["difficulty"]}" data-color="{p.get("color","#3b82f6")}">
            {cover_html}
            <div class="info-overlay">
                {plat_badge}
                <div class="game-name">{p["name"]} ({p["platform"]})</div>
                <div class="game-stats">
                    <div class="stat-item"><div class="stat-value">{p["trophies"]}</div><div class="stat-label">трофеев</div></div>
                    <div class="stat-item"><div class="stat-value">{p["time"]}</div><div class="stat-label">время</div></div>
                    <div class="stat-item"><div class="stat-value">{p["difficulty"]}</div><div class="stat-label">сложность</div></div>
                </div>
                <div style="display: flex; gap: 8px; justify-content: center; margin-top: 8px;">
                    <a class="share-btn" href="{share_url}" target="_blank" title="Поделиться в Telegram">
                        📤 Поделиться
                    </a>
                    {proof_button}
                </div>
            </div>
        </div>''')
    return "\n".join(lines)

def generate_table(platinums: List[dict]) -> str:
    """Генерирует HTML-таблицу со всеми играми (для модалки)."""
    rows = []
    for p in platinums:
        rows.append(f'''
        <tr>
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
    """Формирует window.allPlatinums для клиентской фильтрации, поиска и калькулятора."""
    games_for_js = []
    for p in platinums:
        # Преобразуем строковые difficulty и time в числа, если они ещё не заданы
        diff_rating = p.get("difficulty_rating")
        if diff_rating is None:
            try:
                diff_rating = float(p.get("difficulty", "3").replace(",", "."))
            except:
                diff_rating = 3.0
        hours = p.get("hours")
        if hours is None:
            # Пытаемся извлечь часы из строки time (например "24 дня" -> 24*4=96)
            time_str = p.get("time", "")
            try:
                if "день" in time_str:
                    days = int(re.search(r'\d+', time_str).group())
                    hours = days * 4
                elif "час" in time_str:
                    hours = int(re.search(r'\d+', time_str).group())
                else:
                    hours = 20
            except:
                hours = 20
        online = p.get("online", False)
        missable = p.get("missable_count", 0)

        games_for_js.append({
            "name": p["name"],
            "platform": p["platform"],
            "trophies": p["trophies"],
            "time": p["time"],
            "difficulty": p["difficulty"],
            "difficulty_rating": diff_rating,
            "hours": hours,
            "online": online,
            "missable_count": missable,
            "color": p.get("color", "#3b82f6"),
            "cover": p.get("cover", ""),
            "proofs": p.get("proofs", [])
        })
    return f'<script>window.allPlatinums = {json.dumps(games_for_js, ensure_ascii=False)};</script>'

def generate_meta_tags(total: int, last_name: str, last_time: str) -> str:
    """Мета-теги для SEO и соцсетей."""
    description = f"Выбиваю платиновые трофеи на PS4/PS5 вручную. Уже {total} платин. Без читов, официальный шейринг. От 1500₽."
    return f'''
    <meta name="description" content="{description}">
    <meta name="keywords" content="платина, трофеи, PS4, PS5, помощь с трофеями, boost, platinum">
    <meta name="author" content="Platinum Boost">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{SITE_URL}">
    <meta property="og:title" content="Platinum Boost — платины PS4/PS5 под ключ">
    <meta property="og:description" content="{description}">
    <meta property="og:image" content="{SITE_URL}/preview.jpg">
    <meta property="twitter:card" content="summary_large_image">
    <meta property="twitter:url" content="{SITE_URL}">
    <meta property="twitter:title" content="Platinum Boost — платины PS4/PS5">
    <meta property="twitter:description" content="{description}">
    <meta property="twitter:image" content="{SITE_URL}/preview.jpg">
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Service",
        "name": "Platinum Boost",
        "description": "{description}",
        "provider": {{ "@type": "Person", "name": "Platinum Booster" }},
        "priceRange": "₽1500 - ₽10000",
        "areaServed": "Worldwide",
        "aggregateRating": {{ "@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "25" }}
    }}
    </script>
    '''

def update_html(platinums: List[dict], mapping: Dict[str, GameImages]) -> None:
    if not os.path.exists(HTML_FILE):
        print(f"❌ Шаблон {HTML_FILE} не найден!")
        return

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Карусель (8 случайных)
    carousel_plats = random.sample(platinums, min(CAROUSEL_COUNT, len(platinums)))
    slides_html = generate_slides(carousel_plats, mapping)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ СЛАЙДЫ ЗДЕСЬ -->', slides_html)

    # Таблица всех игр
    table_html = generate_table(platinums)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ ТАБЛИЦУ ЗДЕСЬ -->', table_html)

    # JS-данные
    js_data = generate_js_data(platinums)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ JS ДАННЫЕ -->', js_data)

    # Счётчик, последняя платина, дата
    total = len(platinums)
    last_game = platinums[0]
    last_name = last_game["name"]
    last_time = last_game["time"]
    now_utc = datetime.utcnow().strftime('%d.%m.%Y, %H:%M UTC')

    html = re.sub(r'Уже \d+ платин', f'Уже {total} платин', html)
    html = re.sub(r'<strong id="lastPlatName">.*?</strong>', f'<strong id="lastPlatName">{last_name}</strong>', html)
    html = re.sub(r'<span id="lastPlatTime">.*?</span>', f'<span id="lastPlatTime">{last_time}</span>', html)
    html = re.sub(r'<span id="lastUpdate">.*?</span>', f'<span id="lastUpdate">{now_utc}</span>', html)

    # Мета-теги
    meta_tags = generate_meta_tags(total, last_name, last_time)
    html = html.replace('<!-- GENERATOR.PY ВСТАВИТ МЕТА-ТЕГИ -->', meta_tags)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ index.html обновлён. Всего платин: {total}, в карусели: {len(carousel_plats)} игр.")

def main():
    platinums = load_platinums()
    if not platinums:
        print("❌ Нет данных в data.json, выход.")
        return
    mapping = load_mapping()
    update_html(platinums, mapping)
    print("🎉 Готово!")

if __name__ == "__main__":
    main()