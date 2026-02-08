from flask import Flask, render_template, request, redirect, url_for, session
from stats import player_stats
from encounters import losuj_potwora
from bestiary import bestiariusz_gracza, odkryj_potwora, pokonaj_potwora
from map import mapa_swiata
from enemies import potwory
import random

app = Flask(__name__)
app.secret_key = "tajny_klucz_do_sesji"

# -------------------------------
# Globalne zmienne (plecak + ekwipunek)
# -------------------------------
global_plecak = {
    "miecz": 1,
    "tarcza": 1,
    "helm": 1,
    "zbroja": 1
}

global_ekwipunek = {
    "broń": None,
    "tarcza": None,
    "hełm": None,
    "zbroja": None
}
def uzyj_przedmiot(item_id):
    item = consumables.get(item_id)
    if not item:
        return

    player_stats["hp"] = min(
        player_stats["hp_max"],
        player_stats["hp"] + item["hp"]
    )
    player_stats["energia"] = min(
        player_stats["energia_max"],
        player_stats["energia"] + item["energia"]
    )

    plecak[item_id] -= 1
    if plecak[item_id] <= 0:
        del plecak[item_id]

@app.route('/uzyj/<item_id>', methods=['POST'])
def uzyj(item_id):
    uzyj_przedmiot(item_id)
    return redirect(url_for('gra', zakladka='plecak'))


# -------------------------------
# Walka z potworami
# -------------------------------
@app.route('/walka')
def walka():

    # Jeśli walka już trwa → tylko render
    if "walka" in session:
        walka = session["walka"]
        return render_template(
            "walka.html",
            gracz=walka["gracz"],
            potwor=walka["potwor"],
            tlo_walki=session.get("tlo_walki", "default.png"),
            hp_max=player_stats["hp_max"],
            energia=player_stats["energia"],
            energia_max=player_stats["energia_max"],
            komunikat=None
        )

    # Brak sił
    if player_stats["energia"] <= 0 or player_stats["hp"] <= 0:
        return redirect(url_for("gra", zakladka="mapa"))

    player_stats["energia"] = max(0, player_stats["energia"] - 5)

    # Lokacja
    lokacja = player_stats["lokalizacja"]
    dane_lokacji = mapa_swiata.get(lokacja, {})
    wrogowie_lokacji = dane_lokacji.get("wrogowie", {})
    tlo_walki = dane_lokacji.get("tlo_walki", "default.jpg")

    if not wrogowie_lokacji:
        return redirect(url_for("gra", zakladka="mapa"))

    # Losowanie
    losowy_potwor = losuj_potwora(wrogowie_lokacji)
    if not losowy_potwor:
        return redirect(url_for("gra", zakladka="mapa"))

    potwor = potwory[losowy_potwor].copy()
    potwor["nazwa"] = losowy_potwor

    gracz = {
        "hp": player_stats["hp"],
        "atak": 10 + player_stats["attributes"]["Siła"],
        "obrona": 5 + player_stats["attributes"]["Zręczność"]
    }

    session["log_walki"] = []
    session["walka"] = {"gracz": gracz, "potwor": potwor}
    session["tlo_walki"] = tlo_walki
    session["w_trakcie_walki"] = True

    return redirect(url_for("walka"))

@app.route('/atak', methods=['POST'])
def atak():
    walka_sesja = session.get('walka')
    if not walka_sesja:
        return redirect(url_for('gra'))

    gracz = walka_sesja['gracz']
    potwor = walka_sesja['potwor']

    # Obliczenie obrażeń
    dmg_do_potwora = max(0, gracz["atak"] - potwor["obrona"])
    potwor["hp"] -= dmg_do_potwora

    # Log gracza
    session.setdefault("log_walki", [])
    session["log_walki"].append(f"Zadałeś {dmg_do_potwora} obrażeń.")

    # Obrazenia od potwora
    if potwor["hp"] > 0:
        dmg_do_gracza = max(0, potwor["atak"] - gracz["obrona"])
        gracz["hp"] -= dmg_do_gracza
        session["log_walki"].append(f"Wróg zadał {dmg_do_gracza} obrażeń.")

    # Aktualizacja stanu gracza
    player_stats["hp"] = max(0, gracz["hp"])
    session['walka'] = {"gracz": gracz, "potwor": potwor}

    # Sprawdzenie zakończenia walki
    if potwor["hp"] <= 0:
        player_stats["exp"] += potwor["exp"]

        # 🔥 DROP
        for item in potwor.get("drop", []):
            if random.random() <= item.get("szansa", 1):
                nazwa = item["nazwa"]
                global_plecak[nazwa] = global_plecak.get(nazwa, 0) + 1


        # 🧠 BESTIARIUSZ
        odkryj_potwora(potwor["nazwa"], potwor)
        pokonaj_potwora(potwor["nazwa"])

        session.pop('walka', None)
        session['w_trakcie_walki'] = False
        session['po_walce'] = True
        session.pop("tlo_walki", None)

        return redirect(url_for('gra', zakladka='odpoczynek'))

    if gracz["hp"] <= 0:
        session.pop('walka')
        session["log_walki"].append("Zostałeś pokonany...")
        return redirect(url_for('gra', zakladka='odpoczynek'))

    return redirect(url_for('walka'))


# -------------------------------
# Widok gry
# -------------------------------
@app.route('/gra')
def gra():
    global global_plecak, global_ekwipunek
    komunikat = request.args.get("komunikat", "")
    zakladka = request.args.get('zakladka', 'odpoczynek')

    # regeneracja przy odpoczynku
    if zakladka == 'odpoczynek':
        player_stats["hp"] = min(player_stats["hp_max"], player_stats["hp"] + 20)
        player_stats["mp"] = min(player_stats["mp_max"], player_stats["mp"] + 15)
        player_stats["energia"] = min(player_stats["energia_max"], player_stats["energia"] + 25)

    zmeczenie = ""
    if player_stats["energia"] <= 0:
        zmeczenie = "Jesteś zbyt zmęczony, żeby się poruszać!"

    context = {
        "hp": player_stats["hp"],
        "hp_max": player_stats["hp_max"],
        "mp": player_stats["mp"],
        "mp_max": player_stats["mp_max"],
        "energia": player_stats["energia"],
        "energia_max": player_stats["energia_max"],
        "exp": player_stats["exp"],
        "exp_max": player_stats["exp_max"],
        "lokalizacja": player_stats["lokalizacja"],
        "attributes": player_stats["attributes"],
        "plecak": global_plecak,
        "ekwipunek": global_ekwipunek,
        "bestiariusz": bestiariusz_gracza,
        "mapa": mapa_swiata,
        "dzien": player_stats["dzien"],
        "godzina": player_stats["godzina"],
        "zmeczenie": zmeczenie,
        "komunikat": komunikat
    }

    if zakladka == 'plecak':
        return render_template('plecak.html', **context)
    elif zakladka == 'ekwipunek':
        return render_template('ekwipunek.html', **context)
    elif zakladka == 'statystyki':
        return render_template('statystyki.html', **context)
    elif zakladka == 'crafting':
        return render_template('crafting.html', **context)
    elif zakladka == 'mapa':
        return render_template('mapa.html', **context)
    elif zakladka == 'bestiariusz':
        return render_template('bestiariusz.html', **context)
    else:
        return render_template('odpoczynek.html', **context)

# -------------------------------
# Poruszanie się po mapie
# -------------------------------
@app.route('/move/<cel>')
def move(cel):
    from encounters import losowe_wydarzenie

    if losowe_wydarzenie() == "walka":
        return redirect(url_for("walka"))

    if player_stats["energia"] <= 0 or player_stats["hp"] <= 0:
        return redirect(url_for('gra', zakladka='mapa'))

    aktualna = player_stats["lokalizacja"]

    if cel not in mapa_swiata[aktualna]["sąsiedzi"]:
        return redirect(url_for('gra', zakladka='mapa'))

    # BLOKADA (np. troll)
    lokacja = mapa_swiata.get(aktualna)
    if lokacja and "blokada" in lokacja:
        blokada = lokacja["blokada"]
        if blokada["aktywna"]:
            return redirect(url_for(
                'gra',
                zakladka='mapa',
                komunikat=blokada["opis"]
            ))

    czas = mapa_swiata[aktualna]["sąsiedzi"][cel]

    # upływ czasu
    player_stats["godzina"] += czas
    while player_stats["godzina"] >= 24:
        player_stats["godzina"] -= 24
        player_stats["dzien"] += 1

    player_stats["lokalizacja"] = cel
    player_stats["energia"] = max(0, player_stats["energia"] - czas * 5)

    # 🔥 AKTYWACJA TROLLA PO WEJŚCIU DO WIOSKI
    if cel == "Wioska Tanari":
        most = mapa_swiata.get("Stary Most")
        if most and "blokada" in most:
            most["blokada"]["aktywna"] = True

    if player_stats["lokalizacja"] == "Stary Most":
        session["w_trakcie_walki"] = True
        blokada = mapa_swiata["Stary Most"]["blokada"]
        if blokada["aktywna"]:
            session["walka"] = {
                "potwor": potwory["Troll"].copy(),
                "gracz": {
                    "hp": player_stats["hp"],
                    "atak": 10 + player_stats["attributes"]["Siła"],
                    "obrona": 5 + player_stats["attributes"]["Zręczność"]
                }
            }

            return redirect(url_for("walka"))


    # BLOKADA losowej walki zaraz po walce
    if session.pop("po_walce", False):
        return redirect(url_for('gra', zakladka='mapa'))

    # LOSOWA WALKA
    if not session.get("w_trakcie_walki", False):
        if random.random() < 0.35:  # 35% szansy
            return redirect(url_for("walka"))

    # jeśli NIE było walki → wracamy do mapy
    return redirect(url_for('gra', zakladka='mapa'))

# -------------------------------
# Start aplikacji
# -------------------------------
if __name__ == '__main__':
    app.run(debug=True)
