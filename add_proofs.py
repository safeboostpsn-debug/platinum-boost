import json
import os

# Путь к вашему data.json
DATA_FILE = "data.json"

# Маппинг: "нормализованное имя игры" -> "имя файла в proofs/"
# (имена файлов даны в том виде, как вы их прислали)
PROOF_MAPPING = {
    "batman: arkham knight": "batman_arkham_knight_proof1.jpg",
    "call of duty modern warfare 2 campaign remastered": "cod_mw2_remastered_proof1.jpg",
    "crysis remastered": "crysis_remastered_proof1.jpg",
    "ghost of tsushima: director's cut": "ghost_of_tsushima_proof1.jpg",
    "infamous first light": "infamous_first_light_proof1.jpg",
    "marvel’s spider-man 2": "marvel_spiderman_2_proof1.jpg",
    "marvel's spider-man remastered": "marvel_spiderman_remastered_proof1.jpg",
    "middle-earth: shadow of mordor - game of the year edition": "shadow_of_mordor_proof1.jpg",
    "one piece: pirate warriors 4": "one_piece_pirate_warriors_4_proof1.jpg",
    "pinball heroes": "pinball_heroes_proof1.jpg",
    "ratchet & clank: rift apart": "ratchet_clank_rift_apart_proof1.jpg",
    "stick fight: the game": "stick_fight_the_game_proof1.jpg",
    "twisted metal 3": "twisted_metal_3_proof1.jpg",
    "twisted metal 4": "twisted_metal_4_proof1.jpg",
}

def normalize_name(name: str) -> str:
    """Приводит название игры к нижнему регистру и убирает лишние символы для сопоставления."""
    return name.lower().replace("’", "'").replace(":", "").replace("-", " ").strip()

def add_proofs_to_data():
    if not os.path.exists(DATA_FILE):
        print(f"❌ {DATA_FILE} не найден.")
        return

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        games = json.load(f)

    updated = 0
    for game in games:
        norm_name = normalize_name(game["name"])
        if norm_name in PROOF_MAPPING:
            proof_file = PROOF_MAPPING[norm_name]
            proof_path = f"proofs/{proof_file}"
            if "proofs" not in game or game["proofs"] != [proof_path]:
                game["proofs"] = [proof_path]
                updated += 1
                print(f"✅ Добавлен proof для: {game['name']} -> {proof_path}")
        else:
            # Если нет скриншота, просто убедимся, что поле существует (пустой массив)
            if "proofs" not in game:
                game["proofs"] = []

    if updated > 0:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(games, f, ensure_ascii=False, indent=2)
        print(f"\n🎉 Обновлено {updated} записей. Сохранено в {DATA_FILE}.")
    else:
        print("😴 Ничего не изменилось – все proofs уже добавлены.")

if __name__ == "__main__":
    add_proofs_to_data()
