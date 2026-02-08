# map.py

mapa_swiata = {
    "Las": {
        "opis": "Gęsty las pełen zwierzyny i tajemnic.",
        "sąsiedzi": {
            "Polana": 1,
            "Ruiny": 2
        },
        "wrogowie": {
            "Wilk": 0.8,
            "Lis": 0.3,
            "Dzik": 0.2
        },
        "tlo_walki": "Mrocznylas.png"
    },

    "Polana": {
        "opis": "Spokojna polana idealna na odpoczynek.",
        "sąsiedzi": {
            "Las": 1,
            "Wioska": 1
        },
        "wrogowie": {
            "Wilk": 0.8,
            "Lis": 0.3,
            "Dzik": 0.2
        },
        "tlo_walki": "Mrocznylas.png"
    },

    "Wioska": {
        "opis": "Mała osada ludzi.",
        "sąsiedzi": {
            "Polana": 1
        },
        "wrogowie": {
            "Wilk": 0.8,
            "Lis": 0.3,
            "Dzik": 0.2
        },
        "tlo_walki": "Mrocznylas.png"
    },

    "Ruiny": {
        "opis": "Stare ruiny – niebezpieczne miejsce.",
        "sąsiedzi": {
            "Las": 2
        },
        "wrogowie": {
            "Wilk": 0.8,
            "Lis": 0.3,
            "Dzik": 0.2
        },
        "tlo_walki": "Mrocznylas.png"
    }
}
