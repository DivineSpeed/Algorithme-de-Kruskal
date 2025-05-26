import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QSlider, QTextEdit, QFrame,
                            QRadioButton, QGroupBox, QMessageBox, QDialog, QStatusBar, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import networkx as nx
import time

# Importer notre code existant
from noyau_kruskal import DisjointSet, ensure_connectivity, create_test_graphs
from visualisation_graphe import CytoscapeGraphView
from comparaison_graphes import GraphCompareDialog, GraphComparisonWindow
from graphe_personnalise import CustomGraphDialog

class KruskalCytoscapeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visualisation de l'Algorithme de Kruskal (Cytoscape.js)")
        self.resize(1280, 900)
        
        # Initialiser les variables
        self.graph = None
        self.graph_type = None
        self.mst_edges = []
        self.current_edge_index = 0
        self.animation_speed = 1.0  # secondes entre les étapes
        self.kruskal_thread = None
        self.current_edge = None
        self.sorted_edges = []
        self.test_graphs = create_test_graphs()
        self.graph_names = [title for _, title, _ in self.test_graphs]
        
        # Configurer l'interface
        self.setup_ui()
        
    def setup_ui(self):
        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Disposition principale
        main_layout = QHBoxLayout(central_widget)
        
        # Panneau gauche pour les contrôles
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_panel.setMaximumWidth(400)
        left_layout = QVBoxLayout(left_panel)
        
        # Sélection du graphe
        graph_group = QGroupBox("Sélection du Graphe")
        graph_layout = QVBoxLayout()
        
        self.graph_combo = QComboBox()
        self.graph_combo.addItems(self.graph_names)
        self.graph_combo.currentIndexChanged.connect(self.load_selected_graph)
        graph_layout.addWidget(self.graph_combo)
        
        self.custom_graph_btn = QPushButton("Créer un Graphe Personnalisé")
        self.custom_graph_btn.clicked.connect(self.create_custom_graph)
        graph_layout.addWidget(self.custom_graph_btn)
        
        graph_group.setLayout(graph_layout)
        left_layout.addWidget(graph_group)
        
        # Contrôles d'animation
        animation_group = QGroupBox("Contrôles d'Animation")
        animation_layout = QVBoxLayout()
        
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Vitesse d'Animation:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)
        self.speed_slider.setMaximum(300)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        animation_layout.addLayout(speed_layout)
        
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Démarrer")
        self.step_btn = QPushButton("Étape")
        self.stop_btn = QPushButton("Arrêter")
        self.reset_btn = QPushButton("Réinitialiser")
        
        self.start_btn.clicked.connect(self.start_animation)
        self.step_btn.clicked.connect(self.step_animation)
        self.stop_btn.clicked.connect(self.stop_animation)
        self.reset_btn.clicked.connect(self.reset_animation)
        
        button_layout.addWidget(self.start_btn)
        button_layout.addWidget(self.step_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addWidget(self.reset_btn)
        animation_layout.addLayout(button_layout)
        
        animation_group.setLayout(animation_layout)
        left_layout.addWidget(animation_group)
        
        # Bouton de comparaison
        self.compare_btn = QPushButton("Comparer les Graphes")
        self.compare_btn.clicked.connect(self.compare_graphs)
        left_layout.addWidget(self.compare_btn)
        
        # Affichage des informations
        info_group = QGroupBox("Informations")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        # Ajouter l'affichage de l'état de l'algorithme AU-DESSUS de l'étiquette des composantes (déplacé vers le haut)
        self.algorithm_status = QTextEdit()
        self.algorithm_status.setReadOnly(True)
        self.algorithm_status.setMaximumHeight(120)
        info_layout.addWidget(self.algorithm_status)
        
        # Ajouter l'étiquette du nombre de composantes après l'affichage de l'état
        self.component_label = QLabel("Composantes Connexes: N/A")
        self.component_label.setStyleSheet("font-weight: bold;")
        info_layout.addWidget(self.component_label)
        
        info_group.setLayout(info_layout)
        left_layout.addWidget(info_group)
        
        # Panneau droit pour la visualisation
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)  # Supprimer les marges pour maximiser l'espace
        
        # Utiliser CytoscapeGraphView au lieu de PlotlyNetworkView
        self.graph_view = CytoscapeGraphView()
        self.graph_view.setMinimumHeight(600)  # Définir une hauteur minimale pour le graphe
        right_layout.addWidget(self.graph_view, 1)  # Donner au widget graphe un facteur d'étirement de 1
        
        # Ajouter les panneaux à la disposition principale
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 1)  # Donner plus d'espace au panneau droit
        
        # Ajouter la barre d'état
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.status_bar.addPermanentWidget(self.progress_bar)
        self.progress_bar.hide()
        
        # Initialiser avec le premier graphe
        if self.graph_names:
            self.graph_combo.setCurrentIndex(0)
            
    def load_selected_graph(self, index):
        if index >= 0:
            self.load_graph(index)
            
    def create_custom_graph(self):
        # Ouvrir la boîte de dialogue de graphe personnalisé
        dialog = CustomGraphDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Obtenir le graphe créé
            custom_graph, graph_name = dialog.get_graph()
            
            if custom_graph:
                # Vérifier si le graphe est déconnecté
                is_disconnected = not nx.is_connected(custom_graph)
                
                # Ajouter le graphe personnalisé à la liste test_graphs
                # Marquer les graphes déconnectés de manière appropriée pour qu'ils ne soient pas automatiquement connectés
                graph_type = f"{graph_name} (Graphe Déconnecté)" if is_disconnected else graph_name
                self.test_graphs.append((custom_graph, graph_type, "Personnalisé"))
                
                # Ajouter au menu déroulant
                self.graph_combo.addItem(graph_type)
                
                # Sélectionner le nouveau graphe
                self.graph_combo.setCurrentIndex(self.graph_combo.count() - 1)
        else:
            # L'utilisateur a annulé
            pass
        
    def update_speed(self):
        # Obtenir la valeur du curseur (10-300)
        slider_value = self.speed_slider.value()
        
        # Convertir en vitesse d'animation en secondes (plus lent = valeur plus élevée)
        # Mapper 10-300 à 2.0-0.1 secondes (inversé)
        self.animation_speed = 2.0 - (slider_value - 10) * (1.9 / 290)
        
        # La vitesse minimale doit être de 0.1 secondes
        self.animation_speed = max(0.1, self.animation_speed)
            
    def start_animation(self):
        if self.graph is None:
            QMessageBox.information(self, "Erreur", "Veuillez sélectionner un graphe d'abord.")
            return
        
        if self.kruskal_thread and self.kruskal_thread.isRunning():
            return
        
        # Disable buttons during animation
        self.start_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Start the algorithm in a separate thread
        self.kruskal_thread = KruskalThread(self.graph, self.animation_speed)
        self.kruskal_thread.update_signal.connect(self.update_visualization)
        self.kruskal_thread.finished_signal.connect(self.animation_finished)
        self.kruskal_thread.start()
        
        # Show progress bar
        self.progress_bar.setMaximum(self.graph.number_of_edges())
        self.progress_bar.setValue(0)
        self.progress_bar.show()
        
        # Update status text
        self.update_info("Exécution de l'algorithme de Kruskal...", "blue")
        
    def update_visualization(self, graph, mst_edges, current_edge_idx, is_accepted):
        # Get the current edge being considered
        edges = []
        for u, v, data in graph.edges(data=True):
            edges.append((u, v, data['weight']))
        edges.sort(key=lambda x: x[2])
        
        # Update progress bar
        self.progress_bar.setValue(current_edge_idx + 1)
        
        if current_edge_idx < len(edges):
            current_edge = edges[current_edge_idx]
            u, v, w = current_edge
            
            # Update the graph with the current state
            self.graph_view.draw_graph(graph, mst_edges, current_edge)
            
            # Determine status based on is_accepted parameter
            if is_accepted:
                # Edge was accepted
                status = f"Ajout de l'arête ({u}, {v}) avec poids {w}"
                color = "green"
            else:
                # Edge was rejected
                status = f"Rejet de l'arête ({u}, {v}) avec poids {w} (créerait un cycle)"
                color = "red"
            
            status_text = f"Étape {current_edge_idx+1}/{len(edges)}: {status}"
            self.update_info(status_text, color)
        else:
            current_edge = None
            self.graph_view.draw_graph(graph, mst_edges, current_edge)
        
        # Count connected components in the MST
        if mst_edges:
            vertices = list(graph.nodes())
            ds = DisjointSet(vertices)
            for u, v, _ in mst_edges:
                ds.union(u, v)
                
            # Count unique representatives (connected components)
            components = set()
            for node in graph.nodes():
                components.add(ds.find(node))
            
            component_count = len(components)
            if component_count > 1:
                self.component_label.setText(f"Composantes Connexes: {component_count} (Forêt)")
            else:
                self.component_label.setText(f"Composantes Connexes: {component_count} (Arbre)")
        else:
            self.component_label.setText("Composantes Connexes: N/A")

    def animation_finished(self, graph, mst_edges, execution_time):
        # Hide progress bar
        self.progress_bar.hide()
        
        # Re-enable buttons
        self.start_btn.setEnabled(True)
        self.step_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Calculate total MST weight
        total_weight = sum(weight for _, _, weight in mst_edges)
        
        # Count connected components
        vertices = list(graph.nodes())
        ds = DisjointSet(vertices)
        for u, v, _ in mst_edges:
            ds.union(u, v)
        
        # Count unique representatives (connected components)
        components = set()
        for node in graph.nodes():
            components.add(ds.find(node))
        component_count = len(components)
        
        # Update status
        if component_count > 1:
            result_type = "Forêt Couvrante Minimale"
        else:
            result_type = "Arbre Couvrant Minimal"
        
        status_text = f"Algorithme terminé en {execution_time:.2f} secondes ! {result_type} trouvé avec:"
        status_text += f"\nPoids total: {total_weight:.2f}"
        status_text += f"\nArêtes dans l'ACM: {len(mst_edges)}/{graph.number_of_edges()}"
        status_text += f"\nComposantes: {component_count}"
        
        # Final message stays blue
        self.update_info(status_text, "blue")
        self.graph_view.draw_graph(graph, mst_edges)
        
        # Update the component label
        if component_count > 1:
            self.component_label.setText(f"Composantes Connexes: {component_count} (Forêt)")
        else:
            self.component_label.setText("Composantes Connexes: 1 (Arbre)")

    def step_animation(self):
        if self.graph is None:
            QMessageBox.information(self, "Erreur", "Veuillez sélectionner un graphe d'abord.")
            return
        
        if self.current_edge_index == 0:
            # Initialize the algorithm
            self.sorted_edges = sorted((self.graph[u][v]['weight'], u, v) for u, v in self.graph.edges())
            self.mst_edges = []
            self.ds = DisjointSet(list(self.graph.nodes()))
            self.total_weight = 0
            self.update_info("Démarrage de l'algorithme de Kruskal...", "blue")
        
        if self.current_edge_index < len(self.sorted_edges):
            weight, u, v = self.sorted_edges[self.current_edge_index]
            current_edge = (u, v, weight)  # Format for visualization
            self.current_edge_index += 1
            
            # Check if adding this edge creates a cycle
            is_accepted = False  # Default is rejected
            if self.ds.find(u) != self.ds.find(v):  # If no cycle formed
                self.ds.union(u, v)  # Union vertices
                self.mst_edges.append((u, v, weight))
                self.total_weight += weight
                status = f"Ajout de l'arête ({u}, {v}) avec poids {weight}"
                color = "green"
                is_accepted = True
            else:
                status = f"Arête ignorée ({u}, {v}) avec poids {weight} (créerait un cycle)"
                color = "red"
            
            status += f"\nPoids actuel de l'ACM: {self.total_weight:.2f}"
            self.update_info(status, color)
            
            # Update visualization
            self.graph_view.draw_graph(self.graph, self.mst_edges, current_edge)
        
        if self.current_edge_index >= len(self.sorted_edges):
            status_text = f"Algorithme terminé ! Poids final de l'ACM: {self.total_weight:.2f}, arêtes: {len(self.mst_edges)}"
            self.update_info(status_text, "blue")
            self.graph_view.draw_graph(self.graph, self.mst_edges)
            
    def stop_animation(self):
        if self.kruskal_thread and self.kruskal_thread.isRunning():
            self.kruskal_thread.stop()
            self.kruskal_thread.wait()
            self.start_btn.setEnabled(True)
            self.step_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            self.progress_bar.hide()
            
            status_text = "Algorithme arrêté par l'utilisateur."
            self.update_info(status_text, "blue")
            
    def reset_animation(self):
        if self.kruskal_thread and self.kruskal_thread.isRunning():
            self.kruskal_thread.stop()
            self.kruskal_thread.wait()
        
        self.mst_edges = []
        self.current_edge_index = 0
        self.current_edge = None
        
        # Re-enable buttons
        self.start_btn.setEnabled(True)
        self.step_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.hide()
        
        if self.graph:
            self.graph_view.draw_graph(self.graph)
            
            status_text = "Animation réinitialisée."
            self.update_info(status_text, "blue")
            
    def compare_graphs(self):
        # Open the graph comparison dialog
        dialog = GraphCompareDialog(self.graph_names, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_graphs = dialog.get_selected_graphs()
            
            # Check if two different graphs were selected
            if selected_graphs[0] == selected_graphs[1]:
                QMessageBox.warning(self, "Sélection Invalide", "Veuillez sélectionner deux graphes différents à comparer.")
                return
                
            # Get the graph objects
            graph1 = self.test_graphs[selected_graphs[0]][0]
            graph2 = self.test_graphs[selected_graphs[1]][0]
            
            # Get the graph names
            graph1_name = self.test_graphs[selected_graphs[0]][1]
            graph2_name = self.test_graphs[selected_graphs[1]][1]
            
            # Get the selected category name
            category_name = dialog.get_selected_category()
            
            # Open the comparison window
            self.comparison_window = GraphComparisonWindow(graph1, graph1_name, graph2, graph2_name, category_name, self)
            self.comparison_window.show()
        
    def update_info(self, text, color="blue"):
        """Update the algorithm status information text with color"""
        # Replace newlines with HTML line breaks for proper formatting
        text = text.replace('\n', '<br>')
        html_text = f"<span style='color: {color}; font-weight: bold;'>{text}</span>"
        self.algorithm_status.setHtml(html_text)
    
    def closeEvent(self, event):
        # Clean up any running threads
        if self.kruskal_thread and self.kruskal_thread.isRunning():
            self.kruskal_thread.stop()
            self.kruskal_thread.wait()
        event.accept()

    def load_graph(self, index):
        # Get the selected graph
        self.graph, self.graph_type, _ = self.test_graphs[index]
        
        # Create a copy of the graph to avoid modifying the original
        self.graph = self.graph.copy()
        
        # For disconnected graphs, don't ensure connectivity
        if "Graphe Déconnecté" not in self.graph_type:
            # Ensure the graph is connected
            self.graph = ensure_connectivity(self.graph)
        
        # Update graph info
        self.update_graph_info()
        
        # Draw the graph
        self.graph_view.draw_graph(self.graph)
        
        # Enable the start button
        self.start_btn.setEnabled(True)
        self.step_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        # Update status text
        status_text = f"Graphe '{self.graph_type}' chargé. Cliquez sur 'Démarrer' pour exécuter l'algorithme de Kruskal."
        self.update_info(status_text, "blue")
        self.component_label.setText("Composantes Connexes: N/A")

    def update_graph_info(self):
        """Update the information about the current graph"""
        info_text = f"Graphe: {self.graph_type}\n\n"
        
        # Add graph description based on type
        if self.graph_type == "Petit Graphe (7 sommets)":
            info_text += "DESCRIPTION\n"
            info_text += "Un petit graphe soigneusement conçu avec différents poids sur les arêtes pour démontrer les concepts fondamentaux de l'ACM.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Traçabilité visuelle parfaite de chaque étape de l'algorithme\n"
            info_text += "• Des choix basés sur les poids qui rendent la logique de décision transparente\n"
            info_text += "• Idéal pour les débutants dans l'apprentissage des algorithmes d'ACM\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Structure simplifiée non représentative des réseaux du monde réel\n"
            info_text += "• Complexité limitée qui ne montre pas les cas particuliers\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Illustre le principe fondamental glouton de l'algorithme de Kruskal:\n"
            info_text += "• Montre comment les arêtes de poids minimal sont toujours sélectionnées en premier\n"
            info_text += "• Démontre la détection de cycle à l'aide de la structure Union-Find\n"
            info_text += "• Prouve que les choix localement optimaux conduisent à un ACM globalement optimal\n"
        elif "Graphe Déconnecté" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Un graphe avec plusieurs composantes isolées ayant des caractéristiques structurelles distinctes.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Démontre la formation d'une Forêt Couvrante Minimale\n"
            info_text += "• Montre le comportement de l'algorithme lorsqu'une connectivité complète est impossible\n"
            info_text += "• Met en évidence la construction d'ACM par composante\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Certaines applications nécessitent des réseaux entièrement connectés\n"
            info_text += "• Le résultat final n'est pas un vrai 'arbre' mais une forêt d'arbres\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Révèle comment l'algorithme de Kruskal gère naturellement les graphes déconnectés:\n"
            info_text += "• Crée automatiquement des ACM indépendants pour chaque composante\n"
            info_text += "• Montre que l'algorithme n'a pas besoin de commencer à partir d'un sommet spécifique\n"
            info_text += "• Démontre que la FCM aura exactement (n-c) arêtes, où n = nombre de\n"
            info_text += "  sommets et c = nombre de composantes connexes\n"
        elif "Grand Graphe" in self.graph_type or "Graphe Aléatoire" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Graphe avec des sommets, arêtes et poids générés de façon stochastique simulant des réseaux imprévisibles.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Teste la robustesse de l'algorithme face à des entrées variées\n"
            info_text += "• Simule des scénarios réalistes avec des topologies imprévisibles\n"
            info_text += "• Démontre l'adaptabilité de l'algorithme à différentes structures\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Structure imprévisible rendant les résultats plus difficiles à anticiper\n"
            info_text += "• Peut générer des cas particuliers inhabituels ou des distributions déséquilibrées\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Démontre la polyvalence et la fiabilité de l'algorithme de Kruskal:\n"
            info_text += "• Montre la capacité de l'algorithme à gérer des distributions de poids arbitraires\n"
            info_text += "• Illustre que les garanties de performance sont valables quelle que soit la structure d'entrée\n"
            info_text += "• Prouve que la sélection gloutonne d'arêtes fonctionne de manière optimale même dans des scénarios aléatoires\n"
        elif "Graphe Complet" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Graphe de densité maximale où chaque sommet est directement connecté à tous les autres sommets.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Offre un choix maximal pour la sélection d'arêtes\n"
            info_text += "• Crée un test de résistance optimal pour la détection de cycles\n"
            info_text += "• Représente des réseaux entièrement connectés dans des applications réelles\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• La densité des arêtes crée de nombreux cycles, ce qui complique la visualisation\n"
            info_text += "• Le taux élevé de rejet peut obscurcir la progression de l'algorithme\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Met en évidence l'efficacité de Kruskal avec une densité d'arêtes élevée:\n"
            info_text += "• Démontre comment l'algorithme écarte la grande majorité des arêtes\n"
            info_text += "• Pour un graphe à n sommets, il rejette précisément (n²-n)/2-(n-1) arêtes\n"
            info_text += "• Montre l'importance cruciale de la contrainte de prévention des cycles\n"
            info_text += "• Illustre pourquoi l'implémentation efficace de Union-Find est importante\n"
        elif "Graphe Circulaire" in self.graph_type or "Graphe Cyclique" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Sommets disposés en un seul chemin circulaire avec exactement deux arêtes par sommet.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Fournit un exemple clair de rupture d'exactement un cycle\n"
            info_text += "• Démontre la suppression minimale d'arêtes pour créer un arbre couvrant\n"
            info_text += "• Structure simple rendant la détection de cycle facilement observable\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Complexité limitée rendant la solution finale de l'ACM prévisible\n"
            info_text += "• Manque les divers modèles de cycles des graphes plus complexes\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Illustre parfaitement la propriété de rupture de cycle de l'algorithme de Kruskal:\n"
            info_text += "• Montre comment exactement une arête doit être supprimée de chaque cycle\n"
            info_text += "• Démontre que l'arête la plus lourde du cycle sera toujours exclue\n"
            info_text += "• Illustre comment la structure Union-Find détecte les cycles potentiels\n"
            info_text += "• Prouve que les ACM garantissent la suppression d'exactement une arête de chaque cycle unique\n"
        elif "Motif ACM en Étoile" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Sommet central connecté directement à tous les autres sommets périphériques.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Représente des topologies de réseau communes comme les architectures client-serveur\n"
            info_text += "• Démontre le cas le plus simple de préservation d'arbre\n"
            info_text += "• Modélise les systèmes en étoile dans les transports et la communication\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Forme déjà un arbre, donc l'algorithme de Kruskal confirme simplement la structure\n"
            info_text += "• Manque de cycles, ne démontre donc pas l'aspect de rejet de l'algorithme\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Montre le comportement de base de l'algorithme de Kruskal:\n"
            info_text += "• Quand un graphe est déjà un arbre (acyclique), l'algorithme de Kruskal le préserve\n"
            info_text += "• Les poids des arêtes comptent uniquement pour l'ordre de traitement, pas pour la structure finale\n"
            info_text += "• Démontre qu'un ACM a exactement (n-1) arêtes pour n sommets\n"
            info_text += "• Illustre le cas trivial où aucun cycle ne doit être détecté ou brisé\n"
        elif "Graphe en Grille" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Structure en treillis régulière imitant les rues d'une ville, les réseaux informatiques ou les réseaux électriques.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Modélise de nombreux systèmes réels avec des modèles de connectivité réguliers\n"
            info_text += "• Crée plusieurs options de chemin entre les sommets\n"
            info_text += "• Possède des structures de cycle prévisibles pour l'analyse d'algorithmes\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• La structure régulière peut conduire à de nombreux chemins de poids similaire\n"
            info_text += "• Peut avoir plusieurs configurations ACM valides avec des poids identiques\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Démontre comment l'algorithme de Kruskal gère les structures en grille:\n"
            info_text += "• Montre comment l'algorithme résout de nombreux cycles de grille\n"
            info_text += "• Crée des motifs intéressants de 'rivière' ou de 'serpent' à travers la grille\n"
            info_text += "• Illustre que l'ACM ne suit pas nécessairement la distance de Manhattan\n"
            info_text += "• Démontre des applications réelles comme la disposition de lignes électriques ou de pipelines\n"
        elif "Graphe Clairsemé" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Ratio arêtes/sommets bas avec une connectivité limitée mais suffisante.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Permet une visualisation claire de la construction de l'ACM\n"
            info_text += "• Montre efficacement les choix d'arêtes critiques\n"
            info_text += "• Facilite la compréhension du déroulement pas à pas\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Nombre limité de choix alternatifs pour les arêtes\n"
            info_text += "• Peut ne pas démontrer pleinement la détection de cycle\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Illustre les aspects fondamentaux de l'algorithme de Kruskal:\n"
            info_text += "• Montre comment le choix d'arêtes basé uniquement sur le poids fonctionne\n"
            info_text += "• Démontre que même avec peu d'options, l'algorithme trouve toujours l'ACM optimal\n"
            info_text += "• Met en évidence la progression étape par étape de l'algorithme\n"
            info_text += "• Permet de visualiser clairement la construction progressive de l'ACM\n"
        elif "Graphe Dense" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Ratio arêtes/sommets élevé créant de nombreux chemins alternatifs entre la plupart des sommets.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Met à l'épreuve les mécanismes de détection de cycle de Kruskal\n"
            info_text += "• Modélise des réseaux hautement interconnectés comme les graphes sociaux\n"
            info_text += "• Crée des scénarios difficiles pour les performances de l'algorithme\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• La distribution dense des arêtes crée une complexité visuelle\n"
            info_text += "• Le taux de rejet élevé peut obscurcir la progression de l'algorithme\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Démontre l'efficacité du filtrage des arêtes dans l'algorithme de Kruskal:\n"
            info_text += "• Montre comment l'algorithme traite efficacement les options de chemin concurrentes\n"
            info_text += "• Illustre que même avec O(n²) arêtes, seules (n-1) sont sélectionnées\n"
            info_text += "• Révèle comment les optimisations Union-Find deviennent critiques à l'échelle\n"
            info_text += "• Démontre que la taille de l'ACM dépend uniquement des sommets, pas du nombre d'arêtes\n"
        elif "Arête Pont" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Graphe contenant une arête critique dont la suppression déconnecterait le graphe.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Démontre l'importance des arêtes critiques dans la connectivité du graphe\n"
            info_text += "• Montre comment l'algorithme de Kruskal identifie et conserve naturellement les ponts\n"
            info_text += "• Illustre les points faibles potentiels dans les réseaux\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Structure spécialisée qui peut ne pas être représentative de tous les graphes\n"
            info_text += "• Réduit le nombre de solutions ACM possibles\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Met en évidence des propriétés importantes des ACM:\n"
            info_text += "• Démontre que toute arête pont doit obligatoirement faire partie de tous les ACM possibles\n"
            info_text += "• Illustre la relation entre les ponts et la connectivité minimale\n"
            info_text += "• Montre l'importance de certaines arêtes pour maintenir la connectivité\n"
        elif "Exemple Classique d'ACM" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Graphe de taille moyenne conçu pour illustrer les scénarios classiques rencontrés dans les problèmes d'ACM.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Fournit un ensemble équilibré de choix et de contraintes pour l'algorithme\n"
            info_text += "• Illustre les cas typiques présentés dans les manuels d'algorithmes\n"
            info_text += "• Combine plusieurs aspects intéressants comme les cycles et les ponts\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Structure plus complexe que les exemples pédagogiques minimaux\n"
            info_text += "• Peut nécessiter plus d'attention pour suivre chaque étape\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Présente les caractéristiques classiques des problèmes d'ACM:\n"
            info_text += "• Montre comment plusieurs cycles interconnectés sont résolus séquentiellement\n"
            info_text += "• Illustre comment certaines décisions initiales influencent les choix ultérieurs\n"
            info_text += "• Démontre l'optimalité globale malgré la prise de décisions locales\n"
            info_text += "• Sert de référence pour comparer d'autres implémentations d'algorithmes\n"
        elif "Poids Négatifs" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Graphe contenant des arêtes avec des valeurs de poids négatives, représentant des gains ou des réductions de coût.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Démontre la flexibilité de l'algorithme de Kruskal avec différents types de poids\n"
            info_text += "• Modélise des scénarios réels où certaines connexions apportent des bénéfices\n"
            info_text += "• Crée des situations où l'algorithme favorise certaines arêtes\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Peut créer des intuitions contre-intuitives pour les débutants\n"
            info_text += "• Les poids négatifs peuvent rendre le suivi mental de l'algorithme plus difficile\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Met en lumière le comportement de l'algorithme avec des poids non standard:\n"
            info_text += "• Montre que Kruskal fonctionne correctement même avec des poids négatifs\n"
            info_text += "• Illustre comment les arêtes de poids négatif sont toujours prioritaires\n"
            info_text += "• Démontre que le principe de tri par poids reste valide quelle que soit la plage de valeurs\n"
            info_text += "• Contraste avec certains autres algorithmes de graphes qui ne supportent pas les poids négatifs\n"
        elif "Graphe Biparti" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Graphe divisé en deux ensembles de sommets où les connexions n'existent qu'entre les ensembles, jamais au sein d'un même ensemble.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Modélise des relations entre deux catégories distinctes d'entités\n"
            info_text += "• Structure claire qui illustre des applications comme l'affectation de ressources\n"
            info_text += "• Facilite la visualisation de correspondances et d'appariements\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Topologie contrainte qui limite certains aspects des tests d'algorithmes\n"
            info_text += "• Ne permet pas l'exploration de tous les types de cycles possibles\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Démontre l'application de Kruskal à des structures spécialisées:\n"
            info_text += "• Illustre comment l'ACM connecte les deux ensembles de manière optimale\n"
            info_text += "• Montre que l'ACM d'un graphe biparti forme un arbre qui préserve la bipartition\n"
            info_text += "• Établit des liens avec des problèmes classiques comme le couplage maximal\n"
            info_text += "• Présente des applications pratiques comme les réseaux d'affectation\n"
        elif "Invariant d'Échelle" in self.graph_type:
            info_text += "DESCRIPTION\n"
            info_text += "Réseau où la distribution des degrés suit une loi de puissance: peu de sommets très connectés et beaucoup de sommets peu connectés.\n\n"
            info_text += "AVANTAGES\n"
            info_text += "• Reproduit la structure de nombreux réseaux réels comme Internet, les réseaux sociaux\n"
            info_text += "• Possède des propriétés émergentes comme l'effet petit monde\n"
            info_text += "• Teste l'algorithme sur des topologies hautement hétérogènes\n\n"
            info_text += "LIMITATIONS\n"
            info_text += "• Structure complexe pouvant rendre difficile le suivi visuel de l'algorithme\n"
            info_text += "• Les hubs très connectés créent des défis pour la visualisation claire des ACM\n\n"
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Illustre l'application de Kruskal à des réseaux complexes du monde réel:\n"
            info_text += "• Montre comment l'algorithme gère naturellement les hubs et les périphéries\n"
            info_text += "• Démontre l'efficacité de Kruskal sur des structures topologiques avancées\n"
            info_text += "• Illustre comment l'ACM peut préserver certaines propriétés structurelles du réseau original\n"
            info_text += "• Fait le lien entre la théorie des graphes et les applications dans les systèmes complexes\n"
        else:
            # Custom graph - provide specific information based on graph properties
            is_custom = any(tag in self.graph_type for tag in ["Personnalisé", "personnalisé"])
            is_disconnected = "Déconnecté" in self.graph_type
            
            info_text += "DESCRIPTION\n"
            info_text += "Graphe personnalisé créé par l'utilisateur "
            if is_disconnected:
                info_text += "avec plusieurs composantes déconnectées.\n\n"
            else:
                info_text += "avec une topologie et des modèles de connectivité uniques.\n\n"
            
            # Calculate graph properties to customize the description
            num_nodes = self.graph.number_of_nodes()
            num_edges = self.graph.number_of_edges()
            max_possible_edges = num_nodes * (num_nodes - 1) // 2
            density = num_edges / max_possible_edges if max_possible_edges > 0 else 0
            
            # Describe graph based on density
            info_text += "AVANTAGES\n"
            if density > 0.7:
                info_text += "• Structure hautement connectée avec de nombreux chemins alternatifs\n"
                info_text += "• Bon pour tester la détection de cycles dans des réseaux denses\n"
            elif density > 0.3:
                info_text += "• Connectivité équilibrée avec des options de chemin modérées\n"
                info_text += "• Représente des scénarios de réseau typiques du monde réel\n"
            else:
                info_text += "• Structure clairsemée avec connectivité limitée\n"
                info_text += "• Démontre des scénarios de sélection d'arêtes minimale\n"
            
            # Add custom insights based on structure
            if is_disconnected:
                info_text += "• Démontre comment l'algorithme de Kruskal gère les composantes déconnectées\n\n"
            else:
                info_text += "• Permet une exploration personnalisée de l'algorithme\n\n"
            
            info_text += "LIMITATIONS\n"
            info_text += "• La structure personnalisée peut ne pas représenter des types de graphes standardisés\n"
            if is_disconnected:
                info_text += "• Le résultat sera une forêt plutôt qu'un seul arbre\n"
            else:
                info_text += "• Peut avoir des comportements uniques non observés dans les exemples des manuels\n"
            info_text += "• La distribution des poids des arêtes peut impacter le comportement de l'algorithme de manière imprévisible\n\n"
            
            info_text += "VALEUR ÉDUCATIVE\n"
            info_text += "Ce graphe personnalisé fournit des insights sur l'algorithme de Kruskal:\n"
            
            if is_disconnected:
                info_text += "• Démontre la formation d'une Forêt Couvrante Minimale\n"
                info_text += "• Montre la construction d'ACM par composante dans des sous-graphes isolés\n"
                info_text += "• Illustre que la FCM finale a (n-c) arêtes, où c est le nombre de composantes\n"
            else:
                info_text += "• Montre comment l'algorithme de Kruskal s'adapte à des structures de graphe uniques\n"
                info_text += "• Démontre que l'ACM aura exactement (n-1) arêtes quel que soit le nombre initial d'arêtes\n"
                info_text += "• Illustre l'interaction entre les poids des arêtes et la structure finale de l'arbre\n"
            
            if density > 0.6:
                info_text += "• Met en évidence une détection de cycle efficace dans des scénarios de connectivité dense\n"
            elif density < 0.3:
                info_text += "• Montre comment même des graphes clairsemés peuvent former des structures de connexion optimales\n"
        
        # Add basic graph statistics
        info_text += "\nSTATISTIQUES DU GRAPHE\n"
        info_text += f"• Sommets: {self.graph.number_of_nodes()}\n"
        info_text += f"• Arêtes: {self.graph.number_of_edges()}\n"
        
        # Check if the graph is connected
        is_connected = nx.is_connected(self.graph)
        info_text += f"• Connexe: {'Oui' if is_connected else 'Non'}\n"
        
        if not is_connected:
            # Count connected components
            components = list(nx.connected_components(self.graph))
            info_text += f"• Composantes Connexes: {len(components)}\n"
            info_text += "• Tailles des Composantes: " + ", ".join([str(len(c)) for c in components]) + "\n"
        
        # Calculate edge weight statistics
        weights = [data['weight'] for _, _, data in self.graph.edges(data=True)]
        if weights:
            info_text += f"• Poids min. des arêtes: {min(weights)}\n"
            info_text += f"• Poids max. des arêtes: {max(weights)}\n"
            info_text += f"• Poids total des arêtes: {sum(weights):.2f}\n"
            info_text += f"• Poids moyen des arêtes: {sum(weights)/len(weights):.2f}\n"
            
        self.info_text.setText(info_text)


class KruskalThread(QThread):
    update_signal = pyqtSignal(object, object, int, bool)  # Graphe, arêtes ACM, indice d'arête, est_acceptée
    finished_signal = pyqtSignal(object, list, float)
    
    def __init__(self, graph, animation_speed):
        super().__init__()
        self.graph = graph
        self.animation_speed = animation_speed
        self.running = True
        
    def run(self):
        start_time = time.time()
        
        # Obtenir toutes les arêtes avec leurs poids
        edges = []
        for u, v, data in self.graph.edges(data=True):
            edges.append((u, v, data['weight']))
        
        # Trier les arêtes par poids
        edges.sort(key=lambda x: x[2])
        
        # Initialiser l'ensemble disjoint
        vertices = list(self.graph.nodes())
        ds = DisjointSet(vertices)
        
        mst_edges = []
        
        # Traiter chaque arête par ordre de poids croissant
        for i, (u, v, weight) in enumerate(edges):
            if not self.running:
                break
                
            # Vérifier si l'ajout de cette arête crée un cycle
            if ds.find(u) != ds.find(v):  # Aucun cycle ne sera formé
                # Ajouter l'arête à l'ACM
                ds.union(u, v)
                mst_edges.append((u, v, weight))
                
                # Émettre un signal pour mettre à jour l'interface avec l'état actuel et l'acceptation
                self.update_signal.emit(self.graph, mst_edges, i, True)  # True = Acceptée
                time.sleep(self.animation_speed)
            else:
                # Émettre un signal pour montrer l'arête rejetée
                self.update_signal.emit(self.graph, mst_edges, i, False)  # False = Rejetée
                time.sleep(self.animation_speed / 2)  # Pause plus courte pour les arêtes rejetées
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Signaler que l'algorithme est terminé
        self.finished_signal.emit(self.graph, mst_edges, execution_time)
    
    def stop(self):
        self.running = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = KruskalCytoscapeApp()
    window.show()
    sys.exit(app.exec_()) 