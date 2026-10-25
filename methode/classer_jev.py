# Classe des posts avec Jev (TypeSafe System One) selon jev/questions.json.
# Chaque post a ses propres questions (texte dans les instructions), le contexte commun est dans le state.
# Cache : jev/cache.jsonl (id_post + empreinte des questions). Journal des couts : jev/journal.jsonl.
# Usage (bibliotheque) : from classer import classer ; reponses = classer({id: texte, ...})
import hashlib, json, os, sys, threading, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))
from reparer import reparer  # noqa: E402

CONF = json.loads((ICI / "questions_jev.json").read_text(encoding="utf-8"))
MODELE = CONF["modele"]
EMPREINTE = hashlib.sha1(json.dumps([CONF["questions"], CONF["contexte_state"], MODELE], sort_keys=True).encode()).hexdigest()[:10]
CACHE, JOURNAL = ICI / "cache.jsonl", ICI / "journal.jsonl"
PLAFOND_USD = 0.50
PAR_APPEL = 12  # posts par requete (8 questions chacun)
verrou = threading.Lock()
depense = [0.0]


def _cache() -> dict:
    if not CACHE.exists():
        return {}
    out = {}
    for l in CACHE.read_text(encoding="utf-8").splitlines():
        r = json.loads(l)
        if r["empreinte"] == EMPREINTE:
            out[r["id"]] = r["rep"]
    return out


def _question(nom: str, q: dict, texte: str) -> dict:
    ins = q["instructions"]
    ins = dict(ins) if isinstance(ins, dict) else {"question": ins}
    ins["post"] = texte
    out = {"type": q["type"], "instructions": ins}
    if "criteria" in q:
        out["criteria"] = q["criteria"]
    return out


def _appel(lot: dict) -> dict:
    questions = {f"{nom}__{pid}": _question(nom, q, txt) for pid, txt in lot.items() for nom, q in CONF["questions"].items()}
    corps = json.dumps({"state": CONF["contexte_state"], "model": MODELE, "questions": questions}).encode()
    req = urllib.request.Request("https://api.typesafe.ai/v1/systemone", data=corps, method="POST", headers={
        "Authorization": f"Bearer {os.environ['TYPESAFE_API_KEY']}", "Content-Type": "application/json",
        "User-Agent": "verif-x-24oct"})
    for essai in range(4):
        try:
            rep = json.loads(urllib.request.urlopen(req, timeout=120).read())
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 ** essai)
                continue
            raise RuntimeError(f"TypeSafe {e.code} : {e.read().decode(errors='ignore')[:300]}")
    else:
        raise RuntimeError("TypeSafe : 4 echecs")
    cout = rep.get("usage", {}).get("input_tokens", 0) * 0.042e-6
    res = {}
    for qid, a in rep["answers"].items():
        nom, pid = qid.split("__", 1)
        res.setdefault(pid, {})[nom] = a["noul"] if "noul" in a else a.get("probabilities")
    with verrou:
        depense[0] += cout
        with JOURNAL.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"posts": len(lot), "tokens": rep.get("usage", {}).get("input_tokens"), "cout": round(cout, 6),
                                "modele": rep.get("model"), "date": time.strftime("%Y-%m-%d %H:%M:%S")}) + "\n")
        with CACHE.open("a", encoding="utf-8") as f:
            for pid, r in res.items():
                f.write(json.dumps({"id": pid, "empreinte": EMPREINTE, "rep": r}) + "\n")
    return res


def classer(textes: dict, threads: int = 6) -> dict:
    """textes : {id_post: texte}. Renvoie {id_post: {question: proba ou probas}}."""
    deja = _cache()
    a_faire = {i: reparer(t) for i, t in textes.items() if i not in deja}
    lots = [dict(list(a_faire.items())[k:k + PAR_APPEL]) for k in range(0, len(a_faire), PAR_APPEL)]
    print(f"{len(textes)} posts, {len(deja & textes.keys()) if isinstance(deja, set) else sum(i in deja for i in textes)} en cache, {len(lots)} appels")
    with ThreadPoolExecutor(threads) as ex:
        for res in ex.map(_appel, lots):
            deja.update(res)
            if depense[0] > PLAFOND_USD:
                raise SystemExit(f"ARRET : plafond Jev {PLAFOND_USD} $ atteint")
    print(f"depense de cette execution : {depense[0]:.4f} $")
    return {i: deja[i] for i in textes if i in deja}


def decision(r: dict, inclure_orleans: bool = False) -> str:
    """Table de decision de questions.json. Renvoie manif / autre / non_tranche."""
    hors = r["trappes"] >= 0.7 or r["autopromo"] >= 0.7 or (not inclure_orleans and r["orleans_rn"] >= 0.7)
    if hors or (r["rue"] < 0.3 and r["reaction"] < 0.3):
        return "autre"
    if (r["rue"] >= 0.7 or r["reaction"] >= 0.7) and r["trappes"] < 0.3 and r["autopromo"] < 0.3 and (inclure_orleans or r["orleans_rn"] < 0.3):
        return "manif"
    return "non_tranche"
