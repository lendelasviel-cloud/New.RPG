# encounters.py
import random

def losowe_wydarzenie():
    return random.choice([
        "walka",
        "nic",
        "nic",
        "nic",
        "skrzynia"
    ])

def losuj_potwora(wrogowie_lokacji):
    if not wrogowie_lokacji:
        return None

    return random.choices(
        list(wrogowie_lokacji.keys()),
        weights=wrogowie_lokacji.values(),
        k=1
    )[0]
