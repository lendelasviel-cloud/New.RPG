bestiariusz_gracza = {}

def odkryj_potwora(monster_id, monster_data):
    if monster_id not in bestiariusz_gracza:
        bestiariusz_gracza[monster_id] = {
            "nazwa": monster_data["nazwa"],
            "pokonany": 0,
            "opis": "Nowo odkryta istota."
        }

def pokonaj_potwora(monster_id):
    if monster_id in bestiariusz_gracza:
        bestiariusz_gracza[monster_id]["pokonany"] += 1
