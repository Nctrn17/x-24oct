"""Recalcule tous les tableaux du README a partir de donnees/posts.csv.

Python 3.10+, bibliotheque standard uniquement.
Usage : python methode/analyse.py
"""
import csv
import math
import random
import statistics as st
from collections import defaultdict
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
random.seed(24)

with open(RACINE / "donnees" / "posts.csv", encoding="utf-8") as f:
    tous = list(csv.DictReader(f))

# Posts originaux (ni retweet, ni reponse), classes manif ou autre.
P = []
for r in tous:
    if r["retweet"] == "1" or r["reponse"] == "1" or r["sujet"] == "non_tranche" or not r["vues"]:
        continue
    ton = {k: float(r[f"ton_{k}"]) for k in ("favorable", "hostile", "neutre")}
    P.append({
        "compte": r["compte"].lower(), "jour": r["jour"], "vues": int(r["vues"]), "manif": r["sujet"] == "manif",
        "media": r["media"] == "1", "police": float(r["p_violences_policieres"]) >= 0.7, "pillage": float(r["p_pillages_degats"]) >= 0.7,
        "ton": max(ton, key=ton.get),
        "interactions": sum(int(r[k] or 0) for k in ("likes", "retweets", "reponses", "citations")),
    })

jours_par_compte = defaultdict(set)
for p in P:
    jours_par_compte[p["compte"]].add(p["jour"])
deux_jours = {c for c, j in jours_par_compte.items() if j == {"17", "24"}}
P = [p for p in P if p["compte"] in deux_jours]
par = defaultdict(list)
for p in P:
    par[(p["compte"], p["jour"])].append(p)
comptes = sorted({p["compte"] for p in P})


def ic(valeurs_bootstrap):
    v = sorted(valeurs_bootstrap)
    return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]


print(f"Posts retenus : {len(P)}, comptes presents les deux jours : {len(comptes)}\n")

# 1. Portee brute
print("## 1. Portee brute\n")
print("| Posts | 17 oct : nombre | 17 oct : vues totales | 17 oct : vues medianes | 24 oct : nombre | 24 oct : vues totales | 24 oct : vues medianes |")
print("|---|---|---|---|---|---|---|")
groupes = [("Manif", lambda p: p["manif"]), ("Manif avec image ou video", lambda p: p["manif"] and p["media"]),
           ("Manif, violences policieres", lambda p: p["manif"] and p["police"]), ("Manif, pillages et degats", lambda p: p["manif"] and p["pillage"]),
           ("Autres posts des memes comptes", lambda p: not p["manif"])]
for nom, f in groupes:
    cel = []
    for j in ("17", "24"):
        v = [p["vues"] for p in P if f(p) and p["jour"] == j]
        cel += [f"{len(v):,}".replace(",", " "), f"{sum(v) / 1e6:.1f} M", f"{st.median(v):,.0f}".replace(",", " ")]
    print(f"| {nom} | " + " | ".join(cel) + " |")
for j in ("17", "24"):
    v = sorted((p["vues"] for p in P if p["manif"] and p["jour"] == j), reverse=True)
    print(f"\n{j} oct : 10 posts manif les plus vus = {sum(v[:10]) / 1e6:.1f} M vues ({sum(v[:10]) / sum(v):.0%} du total), post le plus vu = {v[0] / 1e6:.1f} M")


# 2. Portee relative des posts manif, par compte
def rapport(c, j, tirage=False):
    g = par[(c, j)]
    if tirage:
        g = [random.choice(g) for _ in g]
    m = [p["vues"] for p in g if p["manif"]]
    a = [p["vues"] for p in g if not p["manif"]]
    if len(m) < 3 or len(a) < 3:
        return None
    return st.median(m) / st.median(a)


def evolution(c, tirage=False):
    r17, r24 = rapport(c, "17", tirage), rapport(c, "24", tirage)
    return None if r17 is None or r24 is None else r24 / r17 - 1


print("\n## 2. Vues medianes des posts manif rapportees aux autres posts du meme compte\n")
print("Comptes ayant au moins 3 posts manif et 3 autres posts chaque jour.\n")
print("| Compte | Rapport 17 oct | Rapport 24 oct | Evolution |")
print("|---|---|---|---|")
evo = {c: evolution(c) for c in comptes}
evo = {c: e for c, e in evo.items() if e is not None}
for c, e in sorted(evo.items(), key=lambda x: x[1]):
    print(f"| {c} | {rapport(c, '17'):.2f} | {rapport(c, '24'):.2f} | {e:+.0%} |")
boot = []
for _ in range(2000):
    tir = [e for e in (evolution(random.choice(list(evo)), True) for _ in evo) if e is not None]
    if tir:
        boot.append(st.median(tir))
lo, hi = ic(boot)
print(f"\nEvolution mediane sur {len(evo)} comptes : {st.median(evo.values()):+.0%} (intervalle bootstrap 95 % : {lo:+.0%} ; {hi:+.0%}).")
print(f"Comptes en baisse d'au moins 30 % : {sum(e <= -0.3 for e in evo.values())} sur {len(evo)}.")


# 3. Ecarts de portee entre sortes de posts manif
def ecart(a, b, liste):
    res = {}
    for j in ("17", "24"):
        za, zb = [], []
        for c in liste:
            g = [p for p in par[(c, j)] if p["manif"]]
            if len(g) < 5:
                continue
            med = st.median(math.log(p["vues"]) for p in g)
            za += [math.log(p["vues"]) - med for p in g if a(p) and not b(p)]
            zb += [math.log(p["vues"]) - med for p in g if b(p) and not a(p)]
        if len(za) < 10 or len(zb) < 10:
            return None
        res[j] = st.mean(za) - st.mean(zb)
    return res


print("\n## 3. Ecart de portee entre sortes de posts manif (log des vues relatives au compte et au jour)\n")
print("| Comparaison | Ecart 17 oct | Ecart 24 oct | Evolution | Intervalle bootstrap 95 % |")
print("|---|---|---|---|---|")
for nom, a, b in (("Violences policieres - pillages", lambda p: p["police"], lambda p: p["pillage"]),
                  ("Ton favorable - ton hostile", lambda p: p["ton"] == "favorable", lambda p: p["ton"] == "hostile")):
    e = ecart(a, b, comptes)
    bt = [r["24"] - r["17"] for r in (ecart(a, b, [random.choice(comptes) for _ in comptes]) for _ in range(2000)) if r]
    lo, hi = ic(bt)
    print(f"| {nom} | {e['17']:+.2f} | {e['24']:+.2f} | {e['24'] - e['17']:+.2f} | {lo:+.2f} ; {hi:+.2f} |")


# 4. Interactions pour 100 vues
def taux(c, j, manif):
    v = [100 * p["interactions"] / p["vues"] for p in par[(c, j)] if p["manif"] == manif and p["vues"] >= 200]
    return st.median(v) if len(v) >= 3 else None


def evo_taux(liste):
    out = []
    for c in liste:
        t = [taux(c, j, m) for j in ("17", "24") for m in (True, False)]
        if None in t or min(t) <= 0:
            continue
        out.append(math.log((t[2] / t[3]) / (t[0] / t[1])))
    return out


print("\n## 4. Interactions (likes, retweets, reponses, citations) pour 100 vues\n")
print("| Posts | 17 oct | 24 oct |")
print("|---|---|---|")
for nom, m in (("Manif", True), ("Autres", False)):
    cel = [f"{st.median([100 * p['interactions'] / p['vues'] for p in P if p['manif'] == m and p['jour'] == j and p['vues'] >= 200]):.2f}" for j in ("17", "24")]
    print(f"| {nom} | " + " | ".join(cel) + " |")
v = evo_taux(comptes)
bt = [st.median(r) for r in (evo_taux([random.choice(comptes) for _ in comptes]) for _ in range(2000)) if r]
lo, hi = ic(bt)
print(f"\nEvolution du rapport manif / autres, par compte ({len(v)} comptes) : x{math.exp(st.median(v)):.2f} (intervalle bootstrap 95 % : x{math.exp(lo):.2f} ; x{math.exp(hi):.2f}).")
