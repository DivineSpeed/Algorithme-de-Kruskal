# Documentation Technique - Visualisation de l'Algorithme de Kruskal

## Vue d'ensemble du projet

Cette application éducative vise à illustrer visuellement le fonctionnement de l'algorithme de Kruskal pour trouver l'Arbre Couvrant Minimal (ACM) d'un graphe. L'application offre une interface graphique interactive permettant de visualiser l'algorithme en temps réel, de comparer son comportement sur différents types de graphes, et de créer des graphes personnalisés pour l'expérimentation.

## Architecture du projet

Le projet est organisé en cinq modules principaux :

1. `application_kruskal.py` : Application principale et interface utilisateur
2. `noyau_kruskal.py` : Implémentation de l'algorithme et fonctions utilitaires
3. `visualisation_graphe.py` : Composants de visualisation des graphes
4. `comparaison_graphes.py` : Module de comparaison de graphes
5. `graphe_personnalise.py` : Module de création de graphes personnalisés

## Description détaillée des modules

### 1. application_kruskal.py

#### Classes principales

- **KruskalCytoscapeApp** : Classe principale qui gère l'interface utilisateur et orchestre l'exécution de l'algorithme.
  
  Méthodes importantes :
  - `setup_ui()` : Configuration de l'interface utilisateur
  - `load_graph(index)` : Charge un graphe sélectionné
  - `start_animation()` : Démarre l'animation de l'algorithme
  - `step_animation()` : Exécute une seule étape de l'algorithme
  - `update_visualization()` : Met à jour la visualisation du graphe
  - `update_graph_info()` : Met à jour les informations sur le graphe

- **KruskalThread** : Thread pour exécuter l'algorithme sans bloquer l'interface utilisateur.
  
  Méthodes importantes :
  - `run()` : Exécute l'algorithme de Kruskal en arrière-plan
  - `stop()` : Arrête l'exécution du thread

### 2. noyau_kruskal.py

#### Classes et fonctions principales

- **DisjointSet** : Implémentation de la structure de données "Union-Find".
  
  Méthodes importantes :
  - `find(vertex)` : Trouve le représentant d'un ensemble
  - `union(vertex1, vertex2)` : Unit deux ensembles

- **kruskal_mst(graph)** : Implémentation de l'algorithme de Kruskal.
  
  Paramètres :
  - `graph` : Un objet NetworkX Graph
  
  Retourne :
  - `mst` : Le graphe ACM résultant
  - `total_weight` : Le poids total de l'ACM

- **ensure_connectivity(graph)** : Assure qu'un graphe est connexe.
  
  Paramètres :
  - `graph` : Un objet NetworkX Graph
  
  Retourne :
  - Le graphe modifié qui est maintenant connexe

- **create_test_graphs()** : Crée une variété de graphes de test.
  
  Retourne :
  - Liste de tuples (graphe, nom, fichier_image)

### 3. visualisation_graphe.py

#### Classes principales

- **CytoscapeGraphView** : Widget PyQt5 qui encapsule une visualisation de graphe utilisant Cytoscape.js.
  
  Méthodes importantes :
  - `draw_graph(graph, mst_edges=None, current_edge=None)` : Dessine le graphe et met en évidence l'ACM
  - `reset_view()` : Réinitialise la vue du graphe
  - `update_layout()` : Met à jour la disposition du graphe

### 4. comparaison_graphes.py

#### Classes principales

- **GraphCompareDialog** : Dialogue pour sélectionner des graphes à comparer.
  
  Méthodes importantes :
  - `get_selected_graphs()` : Retourne les indices des graphes sélectionnés
  - `get_selected_category()` : Retourne la catégorie de comparaison sélectionnée

- **GraphComparisonWindow** : Fenêtre affichant une comparaison côte à côte.
  
  Méthodes importantes :
  - `step_animation()` : Exécute une étape de l'algorithme sur les deux graphes
  - `update_insights()` : Met à jour les analyses comparatives
  - `show_final_comparison()` : Affiche la comparaison finale détaillée

#### Catégories de comparaison

Le module définit plusieurs catégories de comparaison prédéfinies :
- Dense vs Clairsemé
- Connexe vs Déconnecté
- ACM Unique vs ACM Multiples
- Distributions des Poids d'Arêtes
- Propriétés Structurelles Différentes

### 5. graphe_personnalise.py

#### Classes principales

- **CustomGraphDialog** : Interface pour créer et modifier des graphes.
  
  Méthodes importantes :
  - `add_node()` : Ajoute un nouveau sommet
  - `add_edge()` : Ajoute une nouvelle arête
  - `generate_nodes()` : Génère automatiquement des sommets
  - `generate_edges()` : Génère des arêtes selon différents modèles
  - `get_graph()` : Retourne le graphe créé

- **GraphDrawingArea** : Zone de visualisation pour le graphe en cours de création.
  
  Méthodes importantes :
  - `update_graph(nodes, edges)` : Met à jour la visualisation du graphe

#### Types de graphes générés

Le module permet de générer automatiquement plusieurs types de graphes :
- Graphe complet
- Arêtes aléatoires (avec contrôle de densité)
- Arbre couvrant minimal
- Cycle/Anneau

## Flux d'exécution typique

1. L'utilisateur démarre l'application (`application_kruskal.py`)
2. L'utilisateur sélectionne un graphe prédéfini ou crée un graphe personnalisé
3. L'utilisateur peut:
   - Exécuter l'algorithme de Kruskal avec animation
   - Exécuter l'algorithme étape par étape
   - Comparer l'exécution sur deux graphes différents

## Aspects techniques notables

1. **Multithreading** : L'algorithme s'exécute dans un thread séparé pour ne pas bloquer l'interface utilisateur
2. **Intégration Python/JavaScript** : La visualisation utilise Cytoscape.js intégré dans PyQt5 via QWebEngineView
3. **Algorithmique** : Implémentation efficace de l'algorithme de Kruskal utilisant une structure de données Union-Find
4. **Génération de graphes** : Diverses méthodes pour créer des graphes avec des propriétés spécifiques