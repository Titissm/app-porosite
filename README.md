# 🪨 Visualiser la porosité

Application Streamlit pédagogique (Sciences de la Terre, L3) avec six outils :

1. **Calcul de la porosité** à partir des masses volumiques ou des volumes.
2. **Empilement de grains 2D** : on joue sur le nombre, la taille et le tri des grains.
3. **Compaction** : porosité en fonction de la profondeur (loi d'Athy).
4. **Perméabilité** : estimation par la relation de Kozeny-Carman (porosité et taille des grains).
5. **Porosité de fracture** : ouverture, espacement et nombre de familles de fractures, avec la perméabilité associée (loi cubique).
6. **Volume de pores d'un réservoir** : surface, épaisseur, net/gross, porosité et saturation en eau.

## Lancer l'application en local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Mettre le projet sur GitHub

```bash
git init
git add app.py requirements.txt README.md
git commit -m "Première version de l'app porosité"
git branch -M main
git remote add origin https://github.com/TON-PSEUDO/porosite-app.git
git push -u origin main
```

(Crée d'abord un dépôt vide `porosite-app` sur github.com.)

## Déployer gratuitement

1. Va sur [share.streamlit.io](https://share.streamlit.io) et connecte ton compte GitHub.
2. Clique sur **Create app**, choisis le dépôt `porosite-app`, la branche `main` et le fichier `app.py`.
3. Clique sur **Deploy** : tu obtiens un lien public à partager.

## Source des données

Paramètres de la loi d'Athy (φ₀ et c) : valeurs indicatives d'après Sclater & Christie (1980).
