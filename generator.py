"""
Читает data.json, генерирует слайды, вставляет в index.html.
"""
import json
import re
import os

DATA_FILE = "data.json"
HTML_FILE = "index.html"

def load_platinums() -> list[dict]:
    if not os.path.exists(DATA_FILE):
        print(f"{DATA_FILE} не найден. Сначала запусти scraper.py")
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def generate_slides(platinums: list[dict]) -> str:
    lines = []
    for p in platinums:
        lines.append(
            f'        <div class="carousel-slide" '
            f'data-game="{p["name"]}" '
            f'data-platform="{p["platform"]}" '
            f'data-trophies="{p["trophies"]}" '
            f'data-time="{p["time"]}" '
            f'data-difficulty="{p["difficulty"]}" '
            f'data-color="{p["color"]}"></div>'
        )
    return "\n".join(lines)

def update_html(slides_html: str, total: int, last_name: str, last_time: str) -> None:
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Заменяем слайды между кнопками и dots
    pattern = r'(<button class="carousel-btn next".*?</button>\s*)(.*?)(\s*<div class="carousel-dots")'
    html = re.sub(pattern, f'\\1\n{slides_html}\n        \\3', html, flags=re.DOTALL)

    # Счётчик
    html = re.sub(r'Уже \d+ платин', f'Уже {total} платин', html)
    # Последняя платина
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
        print("Нет данных для обновления")
        return

    slides_html = generate_slides(platinums)
    update_html(
        slides_html,
        total=len(platinums),
        last_name=platinums[0]["name"],
        last_time=platinums[0]["time"]
    )
    print(f"Готово. {len(platinums)} платин в карусели.")

if __name__ == "__main__":
    main()
