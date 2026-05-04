"""
Скрипт для автоматического обновления галереи платин с сайта stratege.ru.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Правильный URL профиля на stratege.ru
STRATEGE_URL = "https://stratege.ru/playstation/users/sana17/"

HTML_FILE = "index.html"
LOG_FILE = "update_log.txt"

def log(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def fetch_platinums():
    """Заходит на stratege.ru и собирает все игры со 100% завершения."""
    log(f"Запрашиваю {STRATEGE_URL}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(STRATEGE_URL, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        log(f"Ошибка запроса: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    platinums = []

    # Ищем таблицу с играми
    table = soup.select_one("table.games, table")
    if not table:
        log("Таблица с играми не найдена")
        # Выведем часть HTML для отладки
        log(f"Заголовок страницы: {soup.title.text if soup.title else 'нет'}")
        return []

    rows = table.select("tr")

    for row in rows:
        try:
            cells = row.select("td")
            if not cells or len(cells) < 5:
                continue

            # Прогресс — ищем 100%
            progress_cell = cells[5] if len(cells) > 5 else None
            if not progress_cell:
                continue

            progress_text = progress_cell.text.strip()
            if "100%" not in progress_text:
                continue

            # Название игры
            name = cells[0].text.strip()
            name = re.sub(r'\s*\(.*?\)\s*', '', name)

            # Платформа
            platform = cells[2].text.strip() if len(cells) > 2 else ""

            # Трофеи (формат "48/48")
            trophies_text = cells[3].text.strip() if len(cells) > 3 else "?"
            trophy_match = re.search(r'(\d+)/(\d+)', trophies_text)
            trophies = trophy_match.group(2) if trophy_match else "?"

            # Время
            time_str = cells[6].text.strip() if len(cells) > 6 else ""

            platinums.append({
                "name": name,
                "trophies": trophies,
                "time": time_str,
                "platform": platform
            })

        except Exception as e:
            log(f"Ошибка при парсинге строки: {e}")
            continue

    log(f"Найдено платин: {len(platinums)}")
    return platinums[:5]


def generate_gallery_html(platinums):
    if not platinums:
        return """    <!-- Мои платины -->
    <section>
        <div class="container">
            <h2>Мои платины</h2>
            <p style="margin-bottom:8px;">Платины скоро появятся.</p>
            <div class="gallery"></div>
        </div>
    </section>"""

    cards = []
    for p in platinums:
        time_str = f" — {p['time']}" if p['time'] else ""
        plat_str = f" ({p['platform']})" if p['platform'] else ""

        card = f"""            <div class="trophy-card">
                <span class="trophy-icon">🏆</span>
                <strong>{p['name']}{plat_str}</strong>
                <span>{p['trophies']} трофеев{time_str}</span>
            </div>"""
        cards.append(card)

    return f"""    <!-- Мои платины -->
    <section>
        <div class="container">
            <h2>Мои платины</h2>
            <p style="margin-bottom:8px;">Несколько примеров из того, что уже сделано. Обновлено автоматически.</p>
            <div class="gallery">
{chr(10).join(cards)}
            </div>
        </div>
    </section>"""


def update_html(new_gallery):
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    pattern = r'<!-- Мои платины -->.*?</section>'
    updated_html = re.sub(pattern, new_gallery, html, flags=re.DOTALL)

    if updated_html == html:
        log("⚠️ Блок галереи не найден в HTML")
        return False

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)

    log("index.html обновлён")
    return True


def main():
    log("========== ЗАПУСК ==========")
    platinums = fetch_platinums()

    if not platinums:
        log("Платины не найдены. Проверь, открыт ли профиль на stratege.ru")
        return

    gallery = generate_gallery_html(platinums)
    if update_html(gallery):
        log("Галерея обновлена успешно")
    log("========== ЗАВЕРШЕНИЕ ==========")


if __name__ == "__main__":
    main()
