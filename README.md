# Keleier

Les infos du jour en breton, en un bouton. Appli web perso (PWA) à installer sur l'écran d'accueil de l'iPhone.

- `index.html` : l'appli, tout en un fichier.
- `robot/sources.json` : la liste des sources, à modifier pour en ajouter ou en retirer.
- `robot/fetch.py` : le robot, lancé toutes les deux heures par GitHub (`.github/workflows/robot.yml`), écrit `data/journal.json`.

Contexte et décisions : dépôt Egor, `13-Kalonkontent/`.
