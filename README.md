# Visualisation de l'Algorithme de Kruskal

Ce projet est une application interactive pour visualiser et comprendre l'algorithme de Kruskal pour trouver l'Arbre Couvrant Minimal (ACM) d'un graphe.

## Guide d'installation

### Prérequis
- Python 3.7 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'installation

1. **Cloner ou télécharger ce dépôt**
   ```
   git clone https://github.com/DivineSpeed/Algorithme-de-Kruskal.git
   ```
   ou téléchargez et décompressez le fichier ZIP du projet.

2. **Naviguer vers le dossier du projet**
   ```
   cd Algorithme-de-Kruskal
   ```

3. **Installer les dépendances**
   ```
   pip install -r requirements.txt
   ```

## Exécution de l'application

Pour lancer l'application principale :
```
python application_kruskal.py
```

## Exécution simplifiée (Windows)

Pour une installation et exécution en un clic, utilisez simplement le fichier `lancer_kruskal.bat` inclus dans le projet.


## Structure du projet

### application_kruskal.py
**Description** : Application principale avec interface graphique pour visualiser l'algorithme de Kruskal.

**Classes principales** :
- `KruskalCytoscapeApp` : Fenêtre principale de l'application.
- `KruskalThread` : Thread pour exécuter l'algorithme sans bloquer l'interface utilisateur.

**Fonctionnalités clés** :
- Sélection de différents types de graphes prédéfinis
- Visualisation étape par étape de l'algorithme de Kruskal
- Contrôle de la vitesse d'animation
- Informations détaillées sur le graphe et l'ACM

### noyau_kruskal.py
**Description** : Implémentation de base de l'algorithme de Kruskal et fonctions utilitaires pour les graphes.

**Classes et fonctions principales** :
- `DisjointSet` : Structure de données pour la détection efficace des cycles
- `kruskal_mst()` : Algorithme de Kruskal pour trouver l'ACM
- `ensure_connectivity()` : Assure que le graphe est connexe
- `create_test_graphs()` : Crée une variété de graphes de test avec différentes caractéristiques

### visualisation_graphe.py
**Description** : Composants de visualisation des graphes utilisant Cytoscape.js.

**Classes principales** :
- `CytoscapeGraphView` : Widget PyQt5 qui encapsule une visualisation de graphe interactive

**Fonctionnalités clés** :
- Rendu interactif des graphes
- Mise en évidence des arêtes de l'ACM
- Animation de l'algorithme de Kruskal

### comparaison_graphes.py
**Description** : Module pour comparer l'exécution de l'algorithme de Kruskal sur différents types de graphes.

**Classes principales** :
- `GraphCompareDialog` : Dialogue pour sélectionner des graphes à comparer
- `GraphComparisonWindow` : Fenêtre affichant une comparaison côte à côte de l'algorithme sur deux graphes

**Fonctionnalités clés** :
- Comparaisons prédéfinies basées sur des catégories (dense vs clairsemé, connexe vs déconnecté, etc.)
- Visualisation simultanée de deux ACM
- Analyse comparative détaillée

### graphe_personnalise.py
**Description** : Module pour créer et éditer des graphes personnalisés.

**Classes principales** :
- `CustomGraphDialog` : Interface pour créer et modifier des graphes
- `GraphDrawingArea` : Zone de visualisation pour le graphe en cours de création

**Fonctionnalités clés** :
- Ajout/suppression manuelle de sommets et arêtes
- Génération automatique de sommets et arêtes selon différents modèles
- Personnalisation des poids d'arêtes
- Prévisualisation en temps réel du graphe créé
- Option "Poids Aléatoires" pour randomiser tous les poids des arêtes

## Notes d'utilisation

- L'option "Comparer les Graphes" permet de visualiser l'exécution simultanée de l'algorithme sur deux graphes différents
- Les graphes déconnectés produisent une Forêt Couvrante Minimale (FCM) plutôt qu'un ACM
- Vous pouvez créer des graphes personnalisés avec l'option "Créer un Graphe Personnalisé"
- Le bouton "Réinitialiser" permet de recommencer l'animation depuis le début
- L'option "Étape" permet d'exécuter l'algorithme pas à pas manuellement 
