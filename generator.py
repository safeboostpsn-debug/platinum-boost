"""
Генератор слайдов карусели. Использует mapping.json для привязки изображений.
Пути к картинкам должны быть указаны относительно корня репозитория.
"""
import json
import re
import os
from dataclasses import dataclass
from typing import Optional, Dict

DATA_FILE = "data.json"
HTML_FILE = "index.html"
MAPPING_FILE = "mapping.json"

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
        print(f"{MAPPING_FILE} не найден. Использую заглушки.")
        return {}
    with open(MAPPING_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    mapping = {}
    for item in data.get("mappings", []):
        game = item["game"].strip().lower()
        cover = item.get("cover", "")
        icon = item.get("icon", "")
        # Проверяем, что файл существует
        if cover and not os.path.exists(cover):
            print(f"  ⚠ Файл не найден: {cover}")
            cover = ""
        if icon and not os.path.exists(icon):
            print(f"  ⚠ Файл не найден: {icon}")
            icon = ""
        mapping[game] = GameImages(cover=cover or None, icon=icon or None)
    print(f"Загружено маппингов: {len(mapping)}")
    return mapping

def generate_slides(platinums: list[dict], mapping: Dict[str, GameImages]) -> str:
    lines = []
    for p in platinums:
        game_key = p["name"].strip().lower()
        imgs = mapping.get(game_key, GameImages())
        cover = imgs.cover
        icon = imgs.icon

        if cover:
            cover_html = f'<img src="{cover}" style="width:100%;height:140px;object-fit:cover;border-radius:10px 10px 0 0;" alt="{p["name"]}">'
        else:
            letter = p["name"][0].upper() if p["name"] else "?"
            color = p.get("color", "#3b82f6")
            cover_html = f'<div style="width:100%;height:140px;background:linear-gradient(135deg,{color}, {color}dd);border-radius:10px 10px 0 0;display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:700;color:rgba(255,255,255,0.4);">{letter}</div>'

        icon_html = ""
        if icon:
            icon_html = f'<img src="{icon}" style="width:24px;height:24px;vertical-align:middle;margin-right:4px;" alt="🏆">'

        lines.append(
            f'        <div class="carousel-slide" '
            f'data-game="{p["name"]}" data-platform="{p["platform"]}" '
            f'data-trophies="{p["trophies"]}" data-time="{p["time"]}" '
            f'data-difficulty="{p["difficulty"]}" data-color="{p["color"]}">'
            f'{cover_html}'
            f'<div style="padding:12px 10px;text-align:center;">'
            f'{icon_html}'
            f'<div style="font-size:13px;font-weight:600;margin:4px 0;">{p["name"]} <span style="color:#888;font-weight:400;">({p["platform"]})</span></div>'
            f'<div style="font-size:12px;color:#888;">{p["trophies"]} трофеев</div>'
            f'<div style="font-size:12px;color:#888;">⏱ {p["time"]} · 📊 {p["difficulty"]}</div>'
            f'</div></div>'
        )
    return "\n".join(lines)

def update_html(slides_html: str, total: int, last_name: str, last_time: str) -> None:
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    pattern = r'(<button class="carousel-btn next".*?</button>\s*)(.*?)(\s*<div class="carousel-dots")'
    html = re.sub(pattern, f'\\1\n{slides_html}\n        \\3', html, flags=re.DOTALL)

    html = re.sub(r'Уже \d+ платин', f'Уже {total} платин', html)
    html = re.sub(
        r'Последняя платина: <strong>.*?</strong>.*',
        f'Последняя платина: <strong>{last_name}</strong> — {last_time}',
        html
    )

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html обновлён. Слайдов: {total}")

def main():
    platinums = load_platinums()
    if not platinums:
        print("Нет данных")
        return

    mapping = load_mapping()
    slides_html = generate_slides(platinums, mapping)
    update_html(slides_html, len(platinums), platinums[0]["name"], platinums[0]["time"])
    print("Готово.")

if __name__ == "__main__":
    main()
