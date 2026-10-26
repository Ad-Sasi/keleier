#!/usr/bin/env python3
"""Le robot : relit les flux de sources.json et écrit data/journal.json pour l'appli.

Le téléphone ne peut pas lire ces flux directement (le serveur ne l'autorise pas),
d'où ce passage intermédiaire. Bibliothèque standard seulement.
"""
import json
import re
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ICI = Path(__file__).resolve().parent
SORTIE = ICI.parent / "data" / "journal.json"
ITUNES = "{http://www.itunes.com/dtds/podcast-1.0.dtd}"


def telecharger(url, essais=3, delai=90):
    # rss.radios.bzh répond lentement : délai long et plusieurs essais
    for n in range(essais):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "kalonkontent-robot/1"})
            with urllib.request.urlopen(req, timeout=delai) as r:
                return r.read()
        except Exception as e:
            print(f"essai {n + 1} raté pour {url} : {e}")
            time.sleep(5)
    return None


def duree_en_secondes(texte):
    if not texte:
        return None
    morceaux = [int(p) for p in texte.strip().split(":") if p.isdigit()]
    s = 0
    for p in morceaux:
        s = s * 60 + p
    return s or None


def episodes(flux, garder):
    brut = telecharger(flux["rss"])
    if brut is None:
        return None
    racine = ET.fromstring(brut)
    sortie = []
    for item in racine.iter("item"):
        enc = item.find("enclosure")
        if enc is None or not enc.get("url"):
            continue
        date = item.findtext("pubDate")
        try:
            iso = parsedate_to_datetime(date).astimezone(timezone.utc).isoformat()
        except Exception:
            iso = None
        texte = (item.findtext("description") or "").strip()
        texte = re.sub(r"<[^>]+>", "", texte)
        sortie.append({
            "id": item.findtext("guid") or enc.get("url"),
            "titre": (item.findtext("title") or flux["nom"]).strip(),
            "date": iso,
            "audio": enc.get("url"),
            "duree": duree_en_secondes(item.findtext(f"{ITUNES}duration")),
            "texte": texte,
        })
    sortie.sort(key=lambda e: e["date"] or "", reverse=True)
    return sortie[:garder]


def main():
    sources = json.loads((ICI / "sources.json").read_text(encoding="utf-8"))
    ancien = {}
    if SORTIE.exists():
        ancien = json.loads(SORTIE.read_text(encoding="utf-8"))

    donnees = {"maj": datetime.now(timezone.utc).isoformat(), "radios": sources["radios"]}
    for cle in ("journal", "reportaj"):
        eps = episodes(sources[cle], sources[cle]["garder"])
        # flux injoignable : on garde la version précédente plutôt qu'une liste vide
        donnees[cle] = {"nom": sources[cle]["nom"], "episodes": eps if eps is not None else ancien.get(cle, {}).get("episodes", [])}
        print(f"{cle} : {len(donnees[cle]['episodes'])} épisodes")

    SORTIE.parent.mkdir(exist_ok=True)
    SORTIE.write_text(json.dumps(donnees, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
