"""Parser log Quake"""

import json

ARMAS = {
    "MOD_ROCKET_SPLASH": "Rocketsplash",
    "MOD_ROCKET": "Foguete",
    "MOD_RAILGUN": "Railgun",
    "MOD_FALLING": "Queda",
    "MOD_SHOTGUN": "Escopeta",
    "MOD_MACHINEGUN": "Metralhadora",
    "MOD_TRIGGER_HURT": "Golpe",
}

jogos = []

players = {}


def read_log(file: str):
    """Read log file"""
    with open(file, "r", encoding="UTF-8") as log:
        for line in log:
            if "InitGame" in line:
                jogos.append({"game": len(jogos) + 1, "status": {"total_kills": 0}})
            elif "ClientUserinfoChanged" in line:
                client_user_info(line)
            elif "Kill:" in line:
                kill_in_game(line)
            elif "ShutdownGame" in line:
                jogos[-1]["status"]["players"] = list(players.values())
                players.clear()


def get_in_text(text: str, separator: str, length: int, position: int) -> str:
    """Get in text"""
    return text.strip().split(separator, length)[position].strip()


def client_user_info(text: str) -> None:
    """Client user info"""
    player_id = int(get_in_text(text, " ", 3, 2))
    player_name = get_in_text(text, "\\", 2, 1)

    if not players.get(player_id):
        players[player_id] = {
            "id": player_id,
            "nome": player_name,
            "kills": 0,
            "old_names": [],
        }
        print(f'* O player "{player_name} entrou no jogo.')
    elif (
        players[player_id].get("nome") != player_name
        and player_name not in players[player_id]["old_names"]
    ):
        last_name = players[player_id]["nome"]
        players[player_id]["nome"] = player_name
        players[player_id]["old_names"].append(last_name)
        print(f'* O player "{last_name}" mudou nome para "{player_name}."')


def kill_in_game(text: str) -> None:
    """Kill in game"""
    player_killer_id = int(get_in_text(text, " ", 3, 2))
    player_killer_name = get_in_text(get_in_text(text, ":", 9, 3), "killed", 2, 0)
    player_victim_id = int(get_in_text(text, " ", 4, 3))
    player_victim_name = get_in_text(get_in_text(text, "killed", 9, 1), "by", 2, 0)
    weapon = get_in_text(text, "by", 2, 1)
    jogos[-1]["status"]["total_kills"] += 1

    if player_killer_id == 1022:
        players[player_victim_id]["kills"] -= 1
        print(
            f'* O player "{player_victim_name}" morreu por que estava ferido e caiu de uma altura que o matou.'
        )
    elif player_killer_name == player_victim_name:
        print(f'* O player "{player_victim_name}" se matou com "{ARMAS.get(weapon)}".')
    else:
        print(
            f'* O player "{player_killer_name}" matou o player "{player_victim_name}" usando a arma "{ARMAS.get(weapon) }".'
        )
        players[player_killer_id]["kills"] += 1


if __name__ == "__main__":
    read_log("Quake.txt")
    with open("log.json", "w", encoding="UTF-8") as json_file:
        json.dump(jogos, json_file, indent=4)
