"""
Скрипт для автоматического обновления галереи платин на сайте.
Заходит на PSNProfiles, собирает платины и вставляет их в index.html.
Запускается через GitHub Actions раз в сутки.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

# Твой PSN ID
PSN_ID = "SASHOK911"
PSN_URL = f"https://psnprofiles.com/{PSN_ID}"

# Файлы
HTML_FILE = "index.html"
LOG_FILE = "update_log.txt"

def log(message):
    """Запись логов с датой и временем."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")

def fetch_platinums():
    """
    Заходит на страницу PSNProfiles и собирает все платины.
    Возвращает список словарей: {name, trophies, time, platform}
    """
    log(f"Запрашиваю {PSN_URL}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,ru;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0"
    }

    try:
        # Сначала заходим на главную, чтобы получить cookies
        session = requests.Session()
        session.get("https://psnprofiles.com", headers=headers, timeout=20)

        # Теперь открываем профиль
        response = session.get(PSN_URL, headers=headers, timeout=30)
        response.raise_for_status()
    except Exception as e:
        log(f"Ошибка запроса: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    platinums = []

    # Ищем строки таблицы с играми
    rows = soup.select("table.zebra tr")

    # Если таблица не найдена — пробуем другие селекторы
    if not rows:
        rows = soup.select("table tr")

    for row in rows:
        try:
            # Пропускаем заголовок таблицы
            if row.select_one("th"):
                continue

            cells = row.select("td")
            if not cells or len(cells) < 2:
                continue

            # Название игры
            name_elem = cells[0].select_one("a.title, a")
            if not name_elem:
                continue
            name = name_elem.text.strip()

            # Пропускаем пустые названия
            if not name:
                continue

            # Ищем платиновый трофей (изображение или иконка)
            plat_elem = row.select_one("img[src*='platinum'], img[alt*='Platinum'], img[title*='Platinum']")
            trophy_icon = row.select_one("span.trophy-platinum, .icon-platinum")

            # Проверяем текст на 100%
            row_text = row.text if row else ""

            is_platinum = plat_elem is not None or trophy_icon is not None or "100%" in row_text

            if not is_platinum:
                continue

            # Парсим трофеи (например, "48/48")
            trophy_match = re.search(r'(\d+)\s*/\s*(\d+)', row_text)
            trophies_total = trophy_match.group(2) if trophy_match else "?"

            # Парсим время
            time_match = re.search(r'(?:за|in)\s+([^·\n]+)', row_text, re.IGNORECASE)
            time_str = time_match.group(1).strip() if time_match else ""

            # Платформа
            platform_span = cells[0].select_one("span.platform, .platform")
            platform = platform_span.text.strip() if platform_span else ""

            platinums.append({
                "name": name,
                "trophies": trophies_total,
                "time": time_str,
                "platform": platform
            })

        except Exception as e:
            log(f"Ошибка при парсинге строки: {e}")
            continue

    log(f"Найдено платин: {len(platinums)}")

    # Берём последние 5 платин
    platinums = platinums[:5]

    # Если платин больше 5 — берём 5 самых свежих (они в начале списка)
    return platinums


def generate_gallery_html(platinums):
    """Генерирует HTML-код галереи из списка платин."""

    if not platinums:
        # Если платин нет — возвращаем заглушку
        return """    <!-- Мои платины -->
    <section>
        <div class="container">
            <h2>Мои платины</h2>
            <p style="margin-bottom:8px;">Платины скоро появятся. Идёт сбор данных с PSNProfiles.</p>
            <div class="gallery">
            </div>
        </div>
    </section>"""

    cards = []
    for p in platinums:
        time_str = f" — {p['time']}" if p['time'] else ""
        platform_str = f" ({p['platform']})" if p['platform'] else ""

        card = f"""            <div class="trophy-card">
                <span class="trophy-icon">🏆</span>
                <strong>{p['name']}{platform_str}</strong>
                <span>{p['trophies']} трофеев{time_str}</span>
            </div>"""
        cards.append(card)

    gallery = f"""    <!-- Мои платины -->
    <section>
        <div class="container">
            <h2>Мои платины</h2>
            <p style="margin-bottom:8px;">Несколько примеров из того, что уже сделано. Обновлено автоматически.</p>
            <div class="gallery">
{chr(10).join(cards)}
            </div>
        </div>
    </section>"""

    return gallery


def update_html(new_gallery):
    """Заменяет блок галереи в index.html на новый."""

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # Ищем блок <!-- Мои платины --> и заменяем всё до закрывающего </section>
    pattern = r'<!-- Мои платины -->.*?</section>'
    replacement = new_gallery

    updated_html = re.sub(pattern, replacement, html, flags=re.DOTALL)

    if updated_html == html:
        log("⚠️ Блок галереи не найден в HTML. Проверь комментарий <!-- Мои платины -->")
        return False

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(updated_html)

    log("index.html успешно обновлён")
    return True


def main():
    log("========== ЗАПУСК ОБНОВЛЕНИЯ ==========")

    platinums = fetch_platinums()

    if not platinums:
        log("Платины не найдены. Проверь настройки приватности PSN.")
        return

    new_gallery = generate_gallery_html(platinums)
    success = update_html(new_gallery)

    if success:
        log("Галерея обновлена успешно")
    else:
        log("Не удалось обновить галерею")

    log("========== ЗАВЕРШЕНИЕ ==========")


if __name__ == "__main__":
    main()
