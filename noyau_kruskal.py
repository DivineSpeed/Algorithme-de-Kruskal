import networkx as nx
import matplotlib.pyplot as plt
import random
from itertools import combinations

# Structure de données "Ensemble disjoint" pour l'algorithme de Kruskal
class DisjointSet:
    def __init__(self, vertices):
        self.parent = {v: v for v in vertices}
        self.rank = {v: 0 for v in vertices}

    def find(self, vertex):
        if self.parent[vertex] != vertex:
            self.parent[vertex] = self.find(self.parent[vertex])  # Compression de chemin
        return self.parent[vertex]

    def union(self, vertex1, vertex2):
        root1 = self.find(vertex1)
        root2 = self.find(vertex2)
        if root1 != root2:
            # Union par rang
            if self.rank[root1] < self.rank[root2]:
                self.parent[root1] = root2
            elif self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root2] = root1
                self.rank[root1] += 1
            return True
        return False

# Algorithme de Kruskal pour trouver l'Arbre Couvrant Minimal
def kruskal_mst(graph):
    edges = sorted((graph[u][v]['weight'], u, v) for u, v in graph.edges())
    vertices = list(graph.nodes())
    ds = DisjointSet(vertices)
    mst_edges = []
    total_weight = 0

    for weight, u, v in edges:
        if ds.union(u, v):
            mst_edges.append((u, v))
            total_weight += weight

    mst = nx.Graph()
    mst.add_nodes_from(vertices)
    mst.add_edges_from(mst_edges)
    return mst, total_weight

# Fonction pour assurer la connectivité du graphe
def ensure_connectivity(graph):
    if nx.is_connected(graph):
        return graph
    # Ajouter des arêtes minimales pour connecter les composantes
    components = list(nx.connected_components(graph))
    for i in range(len(components) - 1):
        u = list(components[i])[0]
        v = list(components[i + 1])[0]
        weight = random.randint(1, 10)  # Poids raisonnable pour éviter de fausser l'ACM
        graph.add_edge(u, v, weight=weight)
    return graph

# Fonction pour vérifier qu'un ACM est acyclique
def is_acyclic(graph):
    try:
        nx.find_cycle(graph)
        return False
    except nx.NetworkXNoCycle:
        return True

# Fonction pour visualiser et enregistrer le graphe et son ACM
def visualize_graph(original_graph, mst, title, filename):
    pos = nx.spring_layout(original_graph, seed=42)
    plt.figure(figsize=(12, 8))

    # Dessiner le graphe original
    nx.draw(original_graph, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=500, font_size=10)
    edge_labels = nx.get_edge_attributes(original_graph, 'weight')
    nx.draw_networkx_edge_labels(original_graph, pos, edge_labels=edge_labels, font_size=8)

    # Mettre en évidence les arêtes de l'ACM en rouge
    nx.draw_networkx_edges(mst, pos, edge_color='red', width=2)

    plt.title(title)
    plt.savefig(filename)
    plt.close()

# Fonction pour créer tous les graphes de test (originaux + complexes)
def create_test_graphs():
    graphs = []

    # Graphe 1: Petit graphe manuel (7 sommets)
    G1 = nx.Graph()
    G1.add_nodes_from(range(7))
    edges1 = [(0, 1, 4), (0, 2, 3), (1, 2, 5), (1, 3, 2), 
              (2, 4, 6), (3, 4, 3), (3, 5, 4), (4, 6, 2), (5, 6, 5)]
    G1.add_weighted_edges_from(edges1)
    graphs.append((G1, "Petit Graphe (7 sommets)", "graphF1.png"))

    # Graphe 2: Graphe de taille moyenne (12 sommets) - Exemple classique d'ACM
    G2 = nx.Graph()
    G2.add_nodes_from(range(12))
    edges2 = [(0, 1, 4), (0, 2, 3), (1, 3, 2), (1, 4, 5), 
              (2, 5, 6), (3, 6, 3), (3, 7, 4), (4, 8, 2), 
              (5, 9, 3), (6, 10, 5), (7, 10, 4), (8, 11, 6),
              (9, 11, 2), (10, 11, 3), (0, 5, 7), (1, 8, 6),
              (2, 9, 5), (3, 10, 8), (4, 11, 7)]
    G2.add_weighted_edges_from(edges2)
    graphs.append((G2, "Exemple Classique d'ACM (12 sommets)", "graphF2.png"))

    # Graphe 3: Graphe de taille moyenne (15 sommets) - Clairsemé avec ACM unique
    G3 = nx.Graph()
    G3.add_nodes_from(range(15))
    # Créer un arbre pour garantir un ACM unique
    for i in range(1, 15):
        G3.add_edge(i//2, i, weight=i)
    # Ajouter quelques arêtes supplémentaires avec des poids plus élevés
    additional_edges = [(0, 3, 15), (1, 5, 12), (2, 7, 14), 
                        (4, 10, 16), (6, 11, 13), (8, 14, 15)]
    G3.add_weighted_edges_from(additional_edges)
    graphs.append((G3, "Graphe Clairsemé avec ACM Unique (15 sommets)", "graphF3.png"))

    # Graphe 4: Graphe de taille moyenne (10 sommets) - Dense avec plusieurs ACM potentiels
    G4 = nx.Graph()
    G4.add_nodes_from(range(10))
    # Créer une structure de base
    for i in range(9):
        G4.add_edge(i, i+1, weight=5)  # Toutes les arêtes du cycle ont un poids égal
    G4.add_edge(0, 9, weight=5)  # Compléter le cycle
    # Ajouter des arêtes supplémentaires avec des poids variés
    for i in range(10):
        for j in range(i+2, min(i+5, 10)):
            if j % 10 != i:  # Éviter les boucles sur soi-même
                G4.add_edge(i, j % 10, weight=random.randint(4, 10))
    graphs.append((G4, "Graphe Dense avec Multiples ACM (10 sommets)", "graphF4.png"))

    # Graphe 5: Graphe déconnecté avec des composantes distinctes (20 sommets)
    G5 = nx.Graph()
    G5.add_nodes_from(range(20))
    # Créer 4 composantes séparées avec des structures plus complexes

    # Composante 1: Un petit graphe complet (K4)
    for i in range(4):
        for j in range(i+1, 4):
            G5.add_edge(i, j, weight=random.randint(1, 7))

    # Composante 2: Une structure similaire à un arbre binaire
    edges_comp2 = [(4, 5, 2), (4, 6, 3), (5, 7, 4), (5, 8, 2), (6, 9, 5), (6, 10, 1)]
    G5.add_weighted_edges_from(edges_comp2)

    # Composante 3: Un cycle avec des cordes
    cycle_edges = [(11, 12, 3), (12, 13, 4), (13, 14, 2), (14, 15, 5), (15, 11, 6)]
    chord_edges = [(11, 13, 7), (12, 15, 8)]
    G5.add_weighted_edges_from(cycle_edges + chord_edges)

    # Composante 4: Une étoile avec un satellite
    star_edges = [(16, 17, 1), (16, 18, 2), (16, 19, 3)]
    satellite_edge = [(19, 17, 9)]  # Crée un petit cycle dans l'étoile
    G5.add_weighted_edges_from(star_edges + satellite_edge)

    graphs.append((G5, "Graphe Déconnecté Complexe (20 sommets, 4 composantes)", "graphF5.png"))

    # Graphe 6: Graphe avec des poids négatifs (12 sommets)
    G6 = nx.Graph()
    G6.add_nodes_from(range(12))
    # Créer une structure de base
    for i in range(11):
        G6.add_edge(i, i+1, weight=random.randint(-5, 5))
    # Ajouter quelques arêtes transversales
    cross_edges = [(0, 5, -3), (0, 6, 2), (1, 7, -4), (2, 8, -2), 
                  (3, 9, 3), (4, 10, -5), (5, 11, 4)]
    G6.add_weighted_edges_from(cross_edges)
    graphs.append((G6, "Graphe avec Poids Négatifs (12 sommets)", "graphF6.png"))

    # Graphe 7: Graphe en grille (16 sommets) - Meilleur pour la visualisation
    G7 = nx.grid_2d_graph(4, 4)  # Grille 4x4
    # Convertir en graphe normal avec des nœuds entiers
    G7 = nx.convert_node_labels_to_integers(G7)
    # Ajouter des poids - faire en sorte que les arêtes horizontales aient des poids plus faibles que les verticales
    for u, v in G7.edges():
        if abs(u-v) == 1:  # Arête horizontale
            G7[u][v]['weight'] = random.randint(1, 5)
        else:  # Arête verticale
            G7[u][v]['weight'] = random.randint(6, 10)
    graphs.append((G7, "Graphe en Grille avec Motif (16 sommets)", "graphF7.png"))

    # Graphe 8: Très grand graphe (50 sommets) - Test de performance
    G8 = nx.Graph()
    G8.add_nodes_from(range(50))
    # Assurer la connectivité
    for i in range(49):
        G8.add_edge(i, i+1, weight=random.randint(1, 10))
    # Ajouter des arêtes supplémentaires
    for _ in range(100):
        u = random.randint(0, 49)
        v = random.randint(0, 49)
        if u != v and not G8.has_edge(u, v):
            G8.add_edge(u, v, weight=random.randint(1, 30))
    graphs.append((G8, "Grand Graphe (50 sommets)", "graphF8.png"))

    # Graphe 9: Graphe circulaire avec connexions transversales (14 sommets)
    G9 = nx.Graph()
    n = 14
    G9.add_nodes_from(range(n))
    # Créer un cercle avec des poids croissants
    for i in range(n):
        G9.add_edge(i, (i+1) % n, weight=i+1)
    # Ajouter quelques arêtes transversales stratégiques avec des poids plus faibles
    cross_edges = [(0, 7, 2), (1, 8, 3), (2, 9, 1), (3, 10, 2), 
                  (4, 11, 1), (5, 12, 3), (6, 13, 2)]
    G9.add_weighted_edges_from(cross_edges)
    graphs.append((G9, "Graphe Circulaire avec Raccourcis Stratégiques (14 sommets)", "graphF9.png"))

    # Graphe 10: Graphe complet avec des poids uniques (10 sommets)
    G10 = nx.complete_graph(10)
    # Générer des poids pour créer un motif spécifique d'ACM (étoile-like)
    weights = {}
    for u, v in G10.edges():
        if u == 0 or v == 0:  # Arêtes connectées au nœud 0 ont un faible poids
            weights[(u, v)] = random.randint(1, 5)
        else:
            weights[(u, v)] = random.randint(10, 20)
    
    nx.set_edge_attributes(G10, values=weights, name='weight')
    graphs.append((G10, "Graphe Complet avec Motif ACM en Étoile (10 sommets)", "graphF10.png"))

    # Graphe 11: Graphe de taille moyenne (15 sommets) avec une arête de pont critique
    G11 = nx.Graph()
    G11.add_nodes_from(range(15))
    # Créer deux sous-graphes denses
    for i in range(7):
        for j in range(i+1, 7):
            G11.add_edge(i, j, weight=random.randint(5, 15))
    
    for i in range(7, 15):
        for j in range(i+1, 15):
            G11.add_edge(i, j, weight=random.randint(5, 15))
    
    # Ajouter un pont avec très faible poids - cet arc sera toujours dans l'ACM
    G11.add_edge(3, 10, weight=1)
    graphs.append((G11, "Graphe avec Arête Pont Critique (15 sommets)", "graphF11.png"))

    # Graphe 12: Graphe avec un piège de cycle proche (12 sommets)
    G12 = nx.Graph()
    G12.add_nodes_from(range(12))
    # Créer un cycle avec des poids décroissants sauf pour une arête
    cycle_edges = [(0, 1, 10), (1, 2, 9), (2, 3, 8), (3, 4, 7),
                  (4, 5, 6), (5, 6, 5), (6, 7, 4), (7, 8, 3),
                  (8, 9, 2), (9, 10, 1), (10, 11, 11), (11, 0, 12)]
    G12.add_weighted_edges_from(cycle_edges)
    graphs.append((G12, "Graphe Cyclique avec Motif de Poids (12 sommets)", "graphF12.png"))

    # Graphe 13: Grand Graphe Biparti (40 sommets)
    G13 = nx.Graph()
    # Créer deux ensembles de nœuds
    set_a = range(0, 20)
    set_b = range(20, 40)
    G13.add_nodes_from(set_a)
    G13.add_nodes_from(set_b)
    # Ajouter des arêtes uniquement entre les ensembles A et B (structure bipartite)
    for a in set_a:
        for b in set_b:
            # Seulement connecter certains nœuds pour garder le graphe gérable
            if (a + b) % 3 == 0:
                G13.add_edge(a, b, weight=random.randint(1, 20))
    graphs.append((G13, "Grand Graphe Biparti (40 sommets)", "graphF13.png"))

    # Graphe 14: Réseau Invariant d'Échelle (60 sommets)
    # Utiliser le modèle Barabási–Albert pour générer un réseau invariant d'échelle
    G14 = nx.barabasi_albert_graph(60, 3, seed=42)
    # Ajouter des poids aux arêtes
    for u, v in G14.edges():
        G14[u][v]['weight'] = random.randint(1, 15)
    graphs.append((G14, "Réseau Invariant d'Échelle (60 sommets)", "graphF14.png"))


    
    return graphs

# Exécution principale
def main():
    random.seed(42)  # Assurer la reproductibilité pour les graphes aléatoires
    test_graphs = create_test_graphs()
    results = []

    for graph, title, filename in test_graphs:
        # Vérifier la connectivité
        if not nx.is_connected(graph):
            print(f"Erreur: {title} n'est pas connecté malgré ensure_connectivity.")
            continue
        mst, total_weight = kruskal_mst(graph)
        # Vérifier que l'ACM est acyclique
        if not is_acyclic(mst):
            print(f"Erreur: L'ACM pour {title} contient un cycle.")
            continue
        visualize_graph(graph, mst, title, filename)
        results.append({
            'title': title,
            'filename': filename,
            'num_vertices': graph.number_of_nodes(),
            'num_edges': graph.number_of_edges(),
            'mst_edges': list(mst.edges()),
            'mst_num_edges': mst.number_of_edges(),
            'total_weight': total_weight,
            'is_acyclic': is_acyclic(mst)
        })

    # Afficher les résultats pour le rapport
    for result in results:
        print(f"\nGraphe: {result['title']}")
        print(f"Nombre de sommets: {result['num_vertices']}")
        print(f"Nombre d'arêtes dans le graphe original: {result['num_edges']}")
        print(f"Arêtes de l'ACM: {result['mst_edges']}")
        print(f"Nombre d'arêtes de l'ACM: {result['mst_num_edges']}")
        print(f"Poids total de l'ACM: {result['total_weight']}")
        print(f"L'ACM est acyclique: {result['is_acyclic']}")
        print(f"Visualisation sauvegardée sous: {result['filename']}")

if __name__ == "__main__":
    main()