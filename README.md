# Énergie, Climat & Forêts au Togo — Dashboard

Tableau de bord interactif Streamlit analysant l'accès à l'électricité, la dépendance
au bois-énergie, les émissions de GES, le climat et les forêts classées du Togo, avec
des recommandations stratégiques pour l'électrification rurale, les énergies propres
et la protection forestière.

## Contenu

- `app.py` — application Streamlit principale (6 onglets)
- `utils.py` — chargement et mise en cache des données
- `clean_data.py` — script de nettoyage des 6 jeux de données bruts vers `data/`
- `data/` — jeux de données nettoyés (CSV + GeoJSON des 53 forêts classées)
- `requirements.txt` — dépendances Python

## Sources de données (opendata.gouv.tg)

1. Indicateurs multisectoriels Togo (Banque mondiale, 1960-2023)
2. Émissions de GES par secteur et type de gaz (2018)
3. Températures mensuelles, 10 villes, 2013-2019
4. Combustibles renouvelables & déchets énergétiques (1971-2014)
5. Émissions CO2 du secteur énergie (1970-2022)
6. Zones protégées / forêts classées (53 forêts, géométries)

## Lancer en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Déployer sur Streamlit Community Cloud

1. Pousser ce dossier dans un dépôt GitHub (ou dézipper puis `git init`)
2. Aller sur https://share.streamlit.io/, connecter le dépôt
3. Renseigner `app.py` comme fichier principal
4. Déployer

## Structure des onglets

1. **Accès à l'électricité** — évolution villes/villages, coupures, délais de raccordement
2. **Énergie des ménages** — bois/charbon/gaz, accès à la cuisson propre, recul forestier
3. **Émissions polluantes** — bilan GES par secteur/gaz (2018), série longue CO2 énergie
4. **Climat** — températures des 10 villes du Sud au Nord (2013-2019)
5. **Aires protégées** — carte interactive des 53 forêts classées
6. **Recommandations** — pistes d'action concrètes par axe
