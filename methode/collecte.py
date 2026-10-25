"""Collecte des posts des comptes suivis, les 17 et 24 octobre 2026, 06h-22h UTC.

Acteur Apify theagents/twitter-scraper (recherche X, onglet Recent), une recherche
`from:<compte> since_time:... until_time:...` par compte et par jour.
Jeton Apify dans la variable d'environnement APIFY_TOKEN.
Usage : python methode/collecte.py methode/comptes.txt sortie/
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ACTEUR = "theagents~twitter-scraper"
FENETRES = {"17": (1792216800, 1792274400), "24": (1792821600, 1792879200)}  # 06:00-22:00 UTC


def lancer(requetes: list[str]) -> list[dict]:
    # maxItems vaut pour le run entier : 400 posts par recherche.
    entree = {"searchTerms": requetes, "maxItems": 400 * len(requetes), "queryType": "Latest"}
    req = urllib.request.Request(
        f"https://api.apify.com/v2/acts/{ACTEUR}/run-sync-get-dataset-items?timeout=290",
        data=json.dumps(entree).encode(), method="POST",
        headers={"Authorization": f"Bearer {os.environ['APIFY_TOKEN']}", "Content-Type": "application/json"})
    return [p for p in json.loads(urllib.request.urlopen(req, timeout=320).read()) if isinstance(p, dict) and p.get("id")]


def main(fichier_comptes: str, sortie: str):
    comptes = [c for c in Path(fichier_comptes).read_text().split() if c]
    requetes = [f"from:{c} since_time:{a} until_time:{b}" for c in comptes for a, b in FENETRES.values()]
    Path(sortie).mkdir(parents=True, exist_ok=True)
    for i in range(0, len(requetes), 10):
        posts = lancer(requetes[i:i + 10])
        Path(sortie, f"lot{i // 10:02d}.json").write_text(json.dumps(posts, ensure_ascii=False), encoding="utf-8")
        print(f"lot {i // 10:02d} : {len(posts)} posts")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
