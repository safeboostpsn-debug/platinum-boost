"""
Генератор слайдов карусели. Выбирает 8 случайных платин из data.json.
"""
import json
import re
import os
import random
from dataclasses import dataclass
from typing import Optional, Dict

DATA_FILE = "data.json"
HTML_FILE = "index.html"
MAPPING_FILE = "mapping.json"
CAROUSEL_COUNT = 8

@dataclass
class GameImages:
    cover: Optional[str] = None
    icon: Optional[str] = None

def load_platinums() -> list[dict]:
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

def generate_slides(platinums: list[dict], mapping: Dict[str, GameImages]) -> str:
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

        icon_html = f'<img src="{icon}" style="width:32px;height:32px;" alt="🏆">' if icon else ''
        plat_badge = f'<div class="plat-badge">{icon_html}<span>Платина</span></div>' if icon else '<div class="plat-badge"><span>🏆 Платина</span></div>'

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
            </div>
        </div>''')
    return "\n".join(lines)

def generate_table(platinums: list[dict]) -> str:
    """Генерирует HTML-таблицу со всеми платинами."""
    rows = []
    for p in platinums:
        rows.append(f'''                    <tr>
                        <td>{p["name"]}</td>
                        <td>{p["platform"]}</td>
                        <td>{p["trophies"]}</td>
                        <td>{p["time"]}</td>
                        <td>{p["difficulty"]}</td>
                    </tr>''')
    return f'''            <table class="all-plat-table">
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

def update_html(slides_html: str, table_html: str, total: int, last_name: str, last_time: str) -> None:
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Вставляем слайды карусели
    pattern = r'(<div class="carousel-slides"[^>]*>)\s*<!-- GENERATOR\.PY ВСТАВИТ СЛАЙДЫ ЗДЕСЬ -->\s*(</div>\s*<button class="carousel-btn prev")'
    if re.search(pattern, html):
        html = re.sub(pattern, f'\\1\n{slides_html}\n        \\2', html, flags=re.DOTALL)
    else:
        pattern = r'(<div class="carousel-slides"[^>]*>)(.*?)(</div>\s*<button class="carousel-btn prev")'
        html = re.sub(pattern, f'\\1\n{slides_html}\n        \\3', html, flags=re.DOTALL)

    # Вставляем таблицу всех платин
    pattern = r'(<div id="allPlatTable"[^>]*>)(.*?)(</div>)'
    if re.search(pattern, html):
        html = re.sub(pattern, f'\\1\n{table_html}\n        \\3', html, flags=re.DOTALL)

    html = re.sub(r'Уже \d+ платин', f'Уже {total} платин', html)
    html = re.sub(r'<strong id="lastPlatName">.*?</strong>', f'<strong id="lastPlatName">{last_name}</strong>', html)
    html = re.sub(r'<span id="lastPlatTime">.*?</span>', f'<span id="lastPlatTime">{last_time}</span>', html)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html обновлён. Слайдов: {total}")

def main():
    platinums = load_platinums()
    if not platinums:
        print("Нет данных")
        return

    mapping = load_mapping()

    # 8 случайных для карусели
    carousel_plats = random.sample(platinums, min(CAROUSEL_COUNT, len(platinums)))
    slides_html = generate_slides(carousel_plats, mapping)

    # Все для таблицы
    table_html = generate_table(platinums)

    last = platinums[0]
    update_html(slides_html, table_html, len(platinums), last["name"], last["time"])
    print("Готово.")

if __name__ == "__main__":
    main()
