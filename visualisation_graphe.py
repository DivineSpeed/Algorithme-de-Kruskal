import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWebEngineWidgets import QWebEngineView
import networkx as nx
import numpy as np
import json
import random
import time
import os

# Importer l'implémentation existante
from noyau_kruskal import create_test_graphs

class CytoscapeGraphView(QWebEngineView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = None
        self.mst_edges = []
        self.current_edge = None
        self.layout_cache = {}
        self.layout_seed = 42
        self.is_initialized = False
        self.is_js_loaded = False
        
        # Créer le modèle HTML avec Cytoscape.js
        self._create_html_template()
        self.loadFinished.connect(self._on_load_finished)
        self.load_html()
        
    def _create_html_template(self):
        # Créer le modèle HTML avec Cytoscape.js
        self.html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Graph Visualization</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                }
                #cy {
                    width: 100%;
                    height: 100vh;
                    margin: 0;
                    padding: 0;
                    position: absolute;
                    bottom: 0;
                    top: 0;
                }
                #controls {
                    position: absolute;
                    top: 10px;
                    right: 10px;
                    background-color: rgba(255, 255, 255, 0.8);
                    padding: 10px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
                    z-index: 10;
                }
                #controls button {
                    margin: 5px;
                    padding: 5px 10px;
                    cursor: pointer;
                }
            </style>
            <script src="https://unpkg.com/cytoscape/dist/cytoscape.min.js"></script>
        </head>
        <body>
            <div id="cy"></div>
            <div id="controls">
                <button id="fitBtn">Fit View</button>
                <button id="resetBtn">Reset Layout</button>
            </div>
            <script>
                // Créer l'instance Cytoscape
                var cy = cytoscape({
                    container: document.getElementById('cy'),
                    layout: {
                        name: 'preset'
                    },
                    style: [
                        {
                            selector: 'node',
                            style: {
                                'label': 'data(label)',
                                'width': 'data(size)',
                                'height': 'data(size)',
                                'background-color': 'data(color)',
                                'color': '#000',
                                'text-valign': 'center',
                                'text-halign': 'center',
                                'font-size': '10px',
                                'text-outline-width': 1,
                                'text-outline-color': '#fff'
                            }
                        },
                        {
                            selector: 'edge',
                            style: {
                                'width': 'data(width)',
                                'line-color': 'data(color)',
                                'curve-style': 'bezier',
                                'label': 'data(weight)',
                                'font-size': '10px',
                                'text-background-color': '#fff',
                                'text-background-opacity': 0.8,
                                'text-background-padding': 2,
                                'text-background-shape': 'roundrectangle'
                            }
                        },
                        {
                            selector: '.mst',
                            style: {
                                'line-color': '#0000FF',
                                'width': 3,
                                'z-index': 2
                            }
                        },
                        {
                            selector: '.current',
                            style: {
                                'line-color': '#FF0000',
                                'line-style': 'dashed',
                                'width': 4,
                                'z-index': 3
                            }
                        }
                    ]
                });
                
                // Configurer les gestionnaires de boutons
                document.getElementById('fitBtn').addEventListener('click', function() {
                    cy.fit();
                });
                
                document.getElementById('resetBtn').addEventListener('click', function() {
                    cy.layout({name: 'preset'}).run();
                });
                
                // Fonction pour mettre à jour les données du graphe
                window.updateGraph = function(graphData) {
                    // Supprimer tous les éléments existants
                    cy.elements().remove();
                    
                    // Ajouter les nouveaux éléments
                    cy.add(graphData);
                    
                    // Appliquer la disposition
                    cy.layout({name: 'preset'}).run();
                    cy.fit();
                }
                
                // Fonction pour mettre à jour les arêtes ACM
                window.updateMST = function(mstEdges) {
                    // Supprimer toutes les classes MST
                    cy.elements('.mst').removeClass('mst');
                    
                    // Ajouter la classe MST aux nouvelles arêtes
                    mstEdges.forEach(function(edgeId) {
                        if (cy.$id(edgeId).length > 0) {
                            cy.$id(edgeId).addClass('mst');
                        }
                    });
                }
                
                // Fonction pour mettre à jour l'arête courante
                window.updateCurrentEdge = function(edgeId) {
                    // Supprimer toutes les classes courantes
                    cy.elements('.current').removeClass('current');
                    
                    // Ajouter la classe courante à l'arête actuelle
                    if (edgeId && cy.$id(edgeId).length > 0) {
                        cy.$id(edgeId).addClass('current');
                    }
                }
                
                // Indiquer que la page est chargée et les fonctions JS sont prêtes
                window.jsReady = true;
            </script>
        </body>
        </html>
        """
        
    def _on_load_finished(self, ok):
        """Appelé quand la page web est chargée"""
        if ok:
            # Vérifier si JS est prêt
            self.page().runJavaScript("window.jsReady !== undefined", self._check_js_ready)
    
    def _check_js_ready(self, result):
        """Vérifier si JavaScript est prêt"""
        self.is_js_loaded = result == True
        if self.is_js_loaded and self.graph:
            # Si JS est prêt et nous avons un graphe, le dessiner
            self.draw_graph(self.graph, self.mst_edges, self.current_edge)
        
    def load_html(self):
        """Charger le modèle HTML"""
        self.setHtml(self.html_template)
        
    def draw_graph(self, graph, mst_edges=None, current_edge=None):
        """Dessiner ou mettre à jour la visualisation du graphe"""
        # Stocker les paramètres pour une utilisation ultérieure si JS n'est pas encore chargé
        self.graph = graph
        self.mst_edges = mst_edges if mst_edges is not None else []
        self.current_edge = current_edge
        
        # Si JS n'est pas encore chargé, attendre l'événement de chargement
        if not self.is_js_loaded:
            return
            
        # Vérifier si nous devons réinitialiser complètement le graphe
        need_full_redraw = (
            id(graph) != id(getattr(self, 'last_graph', None)) or 
            not self.is_initialized
        )
        
        if need_full_redraw:
            self.last_graph = graph
            self.is_initialized = True
            
            # Générer les données du graphe pour Cytoscape.js
            cyto_data = self._generate_cytoscape_data(graph)
            
            # Mettre à jour le graphe
            self._run_js(f"window.updateGraph({json.dumps(cyto_data)});")
            
        # Mettre à jour les arêtes ACM
        mst_edge_ids = self._get_edge_ids_from_edges(mst_edges)
        self._run_js(f"window.updateMST({json.dumps(mst_edge_ids)});")
        
        # Mettre à jour l'arête courante
        current_edge_id = None
        if current_edge:
            if isinstance(current_edge, tuple) and len(current_edge) == 3:
                u, v, _ = current_edge
            else:
                _, u, v = current_edge
            
            # Générer l'ID d'arête
            current_edge_id = self._get_edge_id(u, v)
            
        self._run_js(f"window.updateCurrentEdge({json.dumps(current_edge_id)});")
        
    def _generate_cytoscape_data(self, graph):
        """Générer les données pour Cytoscape.js à partir du graphe NetworkX"""
        # Générer les positions de disposition
        is_disconnected = not nx.is_connected(graph)
        pos = self._generate_layout(graph, is_disconnected)
        
        # Stocker la disposition
        self.layout_cache[id(graph)] = pos
        
        elements = []
        
        # Ajouter les sommets
        num_nodes = graph.number_of_nodes()
        if num_nodes <= 20:
            node_size = 30
            scale_factor = 300  # Plus d'espace entre les sommets pour les petits graphes
        elif num_nodes <= 50:
            node_size = 25
            scale_factor = 250
        else:
            node_size = 20
            scale_factor = 200
            
        for node in graph.nodes():
            x, y = pos[node]
            elements.append({
                'data': {
                    'id': f'n{node}',
                    'label': str(node),
                    'color': 'lightblue',
                    'size': node_size
                },
                'position': {
                    'x': x * scale_factor + 500, # Mettre à l'échelle les positions pour une meilleure visibilité
                    'y': y * scale_factor + 400
                }
            })
            
        # Ajouter les arêtes
        for u, v, data in graph.edges(data=True):
            weight = data['weight']
            edge_id = self._get_edge_id(u, v)
            elements.append({
                'data': {
                    'id': edge_id,
                    'source': f'n{u}',
                    'target': f'n{v}',
                    'weight': str(weight),
                    'color': 'rgba(180, 180, 180, 0.7)',
                    'width': 1.5
                }
            })
            
        return elements
        
    def _get_edge_id(self, u, v):
        """Générer un ID d'arête unique pour Cytoscape"""
        return f'e{min(u, v)}-{max(u, v)}'
        
    def _get_edge_ids_from_edges(self, edges):
        """Convertir la liste d'arêtes en IDs d'arête Cytoscape"""
        edge_ids = []
        
        if not edges:
            return edge_ids
            
        for edge in edges:
            if isinstance(edge, tuple):
                if len(edge) == 3:
                    u, v, _ = edge
                else:
                    u, v = edge
                    
                edge_id = self._get_edge_id(u, v)
                edge_ids.append(edge_id)
                
        return edge_ids
        
    def _generate_layout(self, graph, is_disconnected):
        """Générer les positions de disposition pour le graphe"""
        # Utiliser la disposition mise en cache si disponible pour la cohérence
        graph_id = id(graph)
        if graph_id in self.layout_cache:
            return self.layout_cache[graph_id]
            
        num_nodes = graph.number_of_nodes()
        pos = {}
        
        # Gérer différents types de graphes
        if is_disconnected:
            components = list(nx.connected_components(graph))
            component_count = len(components)
            
            # Placer les composantes dans une disposition en grille avec plus d'espacement
            grid_size = max(2, int(np.ceil(np.sqrt(component_count))))
            grid_width = 3.0 / grid_size  # Augmenté de 2.0 à 3.0
            grid_height = 3.0 / grid_size # Augmenté de 2.0 à 3.0
            
            for i, component in enumerate(components):
                # Calculer la position de la grille
                grid_x = i % grid_size
                grid_y = i // grid_size
                
                # Créer une position pour cette composante
                subgraph = graph.subgraph(component)
                
                # Choisir la disposition appropriée pour la composante
                if len(component) <= 5:
                    sub_pos = nx.circular_layout(subgraph)
                elif len(component) <= 15:
                    sub_pos = nx.spring_layout(subgraph, seed=self.layout_seed + i, 
                                             k=3.0/np.sqrt(len(component)), # Augmenté de 2.0 à 3.0
                                             iterations=150) # Augmenté le nombre d'itérations
                else:
                    sub_pos = nx.kamada_kawai_layout(subgraph, scale=2.0) # Ajout du paramètre scale
                
                # Mettre à l'échelle et décaler la composante à sa position dans la grille
                scale_factor = 0.6 * min(grid_width, grid_height)  # Augmenté de 0.4 à 0.6
                center_x = -1.5 + (grid_x + 0.5) * grid_width  # Point central ajusté
                center_y = -1.5 + (grid_y + 0.5) * grid_height # Point central ajusté
                
                for node, (x, y) in sub_pos.items():
                    pos[node] = (x * scale_factor + center_x, y * scale_factor + center_y)
                    
        elif num_nodes <= 20:
            # Pour les petits graphes, utiliser la disposition Fruchterman-Reingold (layout spring)
            pos = nx.spring_layout(graph, seed=self.layout_seed, 
                                 k=3.0/np.sqrt(num_nodes), # Augmenté de 2.0 à 3.0
                                 iterations=150) # Augmenté le nombre d'itérations
        elif num_nodes <= 50:
            # Pour les graphes moyens, utiliser la disposition Kamada-Kawai avec mise à l'échelle
            pos = nx.kamada_kawai_layout(graph, scale=2.0) # Ajout du paramètre scale
        else:
            # Pour les grands graphes, utiliser Fruchterman-Reingold avec plus d'espace
            pos = nx.spring_layout(graph, seed=self.layout_seed, 
                                 k=4.0/np.sqrt(num_nodes), # Augmenté de 3.0 à 4.0
                                 iterations=100) # Augmenté le nombre d'itérations
            
            # Ajouter un espacement supplémentaire pour les grands graphes
            for node in graph.nodes():
                x, y = pos[node]
                magnitude = np.sqrt(x**2 + y**2)
                if magnitude > 0:
                    # Pousser les sommets plus loin du centre pour un meilleur espacement
                    factor = 1.0 + 0.5 * (1.0 - magnitude)
                    pos[node] = (x * factor, y * factor)
            
        # Mettre en cache la disposition
        self.layout_cache[graph_id] = pos
        return pos
    
    def _run_js(self, script):
        """Exécuter JavaScript dans la vue web"""
        self.page().runJavaScript(script)

    def reset_view(self):
        """Réinitialiser la vue du graphe à un état vide"""
        # Créer des éléments vides
        cyto_data = {
            'nodes': [],
            'edges': []
        }
        
        # Mettre à jour le graphe Cytoscape
        self._run_js(f"window.updateGraph({json.dumps(cyto_data)});")


# Exemple d'utilisation
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Cytoscape Network Graph Test")
    window.resize(1000, 800)
    
    # Créer widget central
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    
    # Créer la vue Cytoscape
    cytoscape_view = CytoscapeGraphView()
    layout.addWidget(cytoscape_view)
    
    # Créer bouton de test
    btn_test = QPushButton("Generate Test Graph")
    layout.addWidget(btn_test)
    
    # Définir comme widget central
    window.setCentralWidget(central_widget)
    
    # Créer un graphe de test
    test_graphs = create_test_graphs()
    
    def on_test_click():
        graph_idx = random.randint(0, len(test_graphs)-1)
        graph, title, _ = test_graphs[graph_idx]
        window.setWindowTitle(f"Cytoscape Network Graph - {title}")
        cytoscape_view.draw_graph(graph)
        
    btn_test.clicked.connect(on_test_click)
    
    window.show()
    on_test_click()  # Dessiner graphe initial
    
    sys.exit(app.exec_()) 