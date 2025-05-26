import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QComboBox, QStatusBar, QSlider, QTextEdit, QFrame,
                            QRadioButton, QGroupBox, QSplitter, QDialog, QButtonGroup,
                            QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer
import networkx as nx
import time

# Importer notre code existant
from noyau_kruskal import DisjointSet
from visualisation_graphe import CytoscapeGraphView

# Catégories de comparaison et leurs descriptions
COMPARISON_CATEGORIES = [
    {
        "name": "Dense vs Clairsemé", 
        "description": "Analysez comment l'algorithme de Kruskal fonctionne sur des graphes denses avec beaucoup d'arêtes versus des graphes clairsemés avec moins d'arêtes",
        "graph_pairs": [(9, 2)]  # Graphe Complet (10) vs Graphe Clairsemé (3)
    },
    {
        "name": "Connexe vs Déconnecté", 
        "description": "Observez comment l'algorithme de Kruskal crée une forêt couvrante minimale au lieu d'un arbre lorsqu'il traite des graphes déconnectés",
        "graph_pairs": [(0, 4)]  # Petit Graphe (1) vs Graphe Déconnecté (5)
    },
    {
        "name": "ACM Unique vs ACM Multiples", 
        "description": "Comparez des graphes où il n'existe qu'une seule solution d'ACM possible versus des graphes avec plusieurs configurations d'ACM équivalentes",
        "graph_pairs": [(2, 3)]  # Graphe ACM Unique (3) vs Graphe ACM Multiples (4)
    },
    {
        "name": "Distributions des Poids d'Arêtes", 
        "description": "Examinez comment la distribution des poids d'arêtes influence les décisions de l'algorithme de Kruskal et la structure finale de l'ACM résultant",
        "graph_pairs": [(8, 6)]  # Graphe Circulaire (9) vs Graphe avec Poids Négatifs (7)
    },
    {
        "name": "Propriétés Structurelles Différentes", 
        "description": "Visualisez comment l'algorithme de Kruskal se comporte sur des graphes avec des caractéristiques topologiques fondamentalement différentes",
        "graph_pairs": [(6, 10)]  # Graphe en Grille (7) vs Graphe avec Arête Pont (11)
    }
]

class GraphCompareDialog(QDialog):
    def __init__(self, graph_names, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparer les Graphes")
        self.resize(650, 450)  # Taille augmentée pour un meilleur affichage des boutons radio
        
        self.graph_names = graph_names
        self.selected_graphs = [-1, -1]  # Par défaut aucune sélection
        self.selected_category_index = 0
        self.selected_category_name = COMPARISON_CATEGORIES[0]["name"]  # Stocker le nom de la catégorie
        
        # Configurer l'interface
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Étiquette de titre avec instructions
        title_label = QLabel("Sélectionnez une Catégorie de Comparaison")
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Créer une zone défilable pour les catégories
        scroll_area = QWidget()
        scroll_layout = QVBoxLayout(scroll_area)
        scroll_layout.setSpacing(12)  # Ajouter plus d'espace entre les éléments
        
        # Créer un groupe de boutons pour les boutons radio
        self.category_group = QButtonGroup()
        
        # Créer des boutons radio stylisés pour chaque catégorie
        for i, category in enumerate(COMPARISON_CATEGORIES):
            # Créer un cadre conteneur pour chaque option
            option_frame = QFrame()
            option_frame.setFrameShape(QFrame.StyledPanel)
            option_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #CCCCCC;
                    border-radius: 5px;
                    background-color: #F5F5F5;
                    margin: 2px;
                    padding: 8px;
                }
                
                QFrame:hover {
                    background-color: #EEEEEE;
                    border: 1px solid #AAAAAA;
                }
            """)
            
            option_layout = QVBoxLayout(option_frame)
            
            # Créer un bouton radio avec le nom de la catégorie
            radio = QRadioButton(category["name"])
            radio.setStyleSheet("""
                QRadioButton {
                    font-size: 12pt;
                    font-weight: bold;
                }
            """)
            
            # Ajouter au groupe de boutons
            self.category_group.addButton(radio, i)
            option_layout.addWidget(radio)
            
            # Ajouter le texte de description
            desc_label = QLabel(category["description"])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("margin-left: 20px;")
            option_layout.addWidget(desc_label)
            
            # Ajouter à la zone défilable
            scroll_layout.addWidget(option_frame)
            
            # Définir la première option comme sélectionnée par défaut
            if i == 0:
                radio.setChecked(True)
        
        # Connecter le signal pour le groupe de boutons
        self.category_group.buttonClicked.connect(self.on_category_selected)
        
        # Ajouter la zone défilable à la disposition principale
        layout.addWidget(scroll_area)
        
        # Affichage des graphes sélectionnés (lecture seule)
        graph_display = QGroupBox("Graphes Sélectionnés")
        graph_display.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                margin-top: 10px;
                padding: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        graph_display_layout = QVBoxLayout(graph_display)
        
        self.graph1_label = QLabel("Premier Graphe: ")
        self.graph1_label.setStyleSheet("font-size: 11pt;")
        self.graph2_label = QLabel("Deuxième Graphe: ")
        self.graph2_label.setStyleSheet("font-size: 11pt;")
        
        graph_display_layout.addWidget(self.graph1_label)
        graph_display_layout.addWidget(self.graph2_label)
        
        layout.addWidget(graph_display)
        
        # Boutons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.setStyleSheet("""
            QPushButton {
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
        """)
        layout.addWidget(button_box)
        
        # Initialiser avec la première catégorie
        self.select_category(0)
        
    def on_category_selected(self, button):
        """Gérer la sélection des boutons radio"""
        self.select_category(self.category_group.id(button))
    
    def select_category(self, index):
        if 0 <= index < len(COMPARISON_CATEGORIES):
            self.selected_category_index = index
            category = COMPARISON_CATEGORIES[index]
            self.selected_category_name = category["name"]  # Stocker le nom de la catégorie
            
            # Mettre à jour l'affichage des graphes sélectionnés
            graph_pair = category["graph_pairs"][0]
            self.selected_graphs = list(graph_pair)
            
            # Mettre à jour les étiquettes
            if 0 <= graph_pair[0] < len(self.graph_names) and 0 <= graph_pair[1] < len(self.graph_names):
                self.graph1_label.setText(f"Premier Graphe: {self.graph_names[graph_pair[0]]}")
                self.graph2_label.setText(f"Deuxième Graphe: {self.graph_names[graph_pair[1]]}")
        
    def accept(self):
        # Utiliser les graphes de la catégorie actuellement sélectionnée
        if 0 <= self.selected_category_index < len(COMPARISON_CATEGORIES):
            self.selected_graphs = list(COMPARISON_CATEGORIES[self.selected_category_index]["graph_pairs"][0])
        
        super().accept()
        
    def get_selected_graphs(self):
        return self.selected_graphs

    def get_selected_category(self):
        return self.selected_category_name

class GraphComparisonWindow(QMainWindow):
    def __init__(self, graph1, graph1_name, graph2, graph2_name, category_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Comparaison Interactive des Graphes")
        self.resize(1280, 900)
        
        # Initialiser les variables
        self.graph1 = graph1
        self.graph2 = graph2
        self.graph1_name = graph1_name
        self.graph2_name = graph2_name
        self.category_name = category_name  # Stocker le nom de la catégorie
        
        self.mst_edges1 = []
        self.mst_edges2 = []
        self.current_edge_index1 = 0
        self.current_edge_index2 = 0
        
        # Trier les arêtes pour les deux graphes
        self.sorted_edges1 = sorted([(u, v, graph1[u][v]['weight']) for u, v in graph1.edges()], 
                                   key=lambda x: x[2])
        self.sorted_edges2 = sorted([(u, v, graph2[u][v]['weight']) for u, v in graph2.edges()], 
                                   key=lambda x: x[2])
        
        # Initialiser DisjointSet pour les deux graphes
        self.ds1 = DisjointSet(list(graph1.nodes()))
        self.ds2 = DisjointSet(list(graph2.nodes()))
        
        self.animation_speed = 1.0  # secondes entre les étapes
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.step_animation)
        
        # Statistiques
        self.stats1 = {
            "edges_considered": 0,
            "edges_accepted": 0,
            "edges_rejected": 0
        }
        self.stats2 = {
            "edges_considered": 0,
            "edges_accepted": 0,
            "edges_rejected": 0
        }
        
        # Configurer l'interface
        self.setup_ui()
        
        # Initialiser les visualisations avec un court délai pour assurer le chargement de JS
        QTimer.singleShot(500, self.init_visualizations)
    
    def init_visualizations(self):
        """Initialiser les visualisations avec un délai pour assurer un chargement correct"""
        self.graph_view1.draw_graph(self.graph1, self.mst_edges1, None)
        self.graph_view2.draw_graph(self.graph2, self.mst_edges2, None)
        
        # Initialiser le panneau d'analyses avec les informations de l'algorithme
        self.update_insights(force_update=True)
        
    def setup_ui(self):
        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # La disposition principale est une disposition verticale
        main_layout = QVBoxLayout(central_widget)
        
        # Section supérieure - Affichages des graphes
        top_section = QSplitter(Qt.Horizontal)
        
        # Panneau gauche pour le graphe
        left_panel = QFrame()
        left_panel.setFrameShape(QFrame.StyledPanel)
        left_layout = QVBoxLayout(left_panel)
        
        # Titre pour le premier graphe
        graph1_title = QLabel(f"<b>{self.graph1_name}</b>")
        graph1_title.setAlignment(Qt.AlignCenter)
        graph1_title.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        left_layout.addWidget(graph1_title)
        
        # Visualisation du graphe 1
        self.graph_view1 = CytoscapeGraphView()
        left_layout.addWidget(self.graph_view1)
        
        # Panneau droit pour le graphe
        right_panel = QFrame()
        right_panel.setFrameShape(QFrame.StyledPanel)
        right_layout = QVBoxLayout(right_panel)
        
        # Titre pour le second graphe
        graph2_title = QLabel(f"<b>{self.graph2_name}</b>")
        graph2_title.setAlignment(Qt.AlignCenter)
        graph2_title.setStyleSheet("font-size: 14px; margin-bottom: 10px;")
        right_layout.addWidget(graph2_title)
        
        # Visualisation du graphe 2
        self.graph_view2 = CytoscapeGraphView()
        right_layout.addWidget(self.graph_view2)
        
        # Ajouter les panneaux au séparateur
        top_section.addWidget(left_panel)
        top_section.addWidget(right_panel)
        top_section.setSizes([640, 640])  # Tailles égales
        
        # Ajouter la section supérieure à la disposition principale
        main_layout.addWidget(top_section, 2)  # 2/3 de l'espace
        
        # Section inférieure - Contrôles et informations
        bottom_section = QFrame()
        bottom_section.setFrameShape(QFrame.StyledPanel)
        bottom_layout = QHBoxLayout(bottom_section)
        
        # Côté gauche - Contrôles
        controls_group = QGroupBox("Contrôles d'Animation")
        controls_layout = QVBoxLayout(controls_group)
        
        # Contrôles de vitesse
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(QLabel("Vitesse:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(10)
        self.speed_slider.setMaximum(300)
        self.speed_slider.setValue(100)
        self.speed_slider.valueChanged.connect(self.update_speed)
        speed_layout.addWidget(self.speed_slider)
        controls_layout.addLayout(speed_layout)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        self.start_btn = QPushButton("Démarrer")
        self.step_btn = QPushButton("Étape par Étape")
        self.stop_btn = QPushButton("Arrêter")
        self.reset_btn = QPushButton("Réinitialiser")
        
        self.start_btn.clicked.connect(self.start_animation)
        self.step_btn.clicked.connect(self.step_animation)
        self.stop_btn.clicked.connect(self.stop_animation)
        self.reset_btn.clicked.connect(self.reset_animation)
        
        self.stop_btn.setEnabled(False)  # Désactivé initialement
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.step_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addWidget(self.reset_btn)
        controls_layout.addLayout(buttons_layout)
        
        # Progression et statistiques supprimées comme demandé
        
        # Côté droit - Analyse
        analysis_group = QGroupBox("Analyse Comparative")
        analysis_layout = QVBoxLayout(analysis_group)
        
        # Zone de texte pour les analyses
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setStyleSheet("font-size: 14px; line-height: 1.4;")
        analysis_layout.addWidget(self.insights_text)
        
        # Le texte d'analyse par défaut n'est pas défini ici - sera défini dans init_visualizations
        
        # Ajouter les deux côtés à la disposition inférieure
        bottom_layout.addWidget(controls_group, 1)
        bottom_layout.addWidget(analysis_group, 2)  # L'analyse obtient plus d'espace
        
        # Ajouter la section inférieure à la disposition principale
        main_layout.addWidget(bottom_section, 1)  # 1/3 de l'espace
        
        # Barre d'état
        self.status_bar = QStatusBar()
        self.status_bar.showMessage("Prêt à analyser les graphes")
        self.setStatusBar(self.status_bar)
        
    def update_stats_display(self):
        """Mettre à jour l'affichage des statistiques"""
        # Les étiquettes de statut ont été supprimées - pas de mises à jour nécessaires ici
        pass
    
    def update_speed(self):
        """Mettre à jour la vitesse d'animation à partir du curseur"""
        # Obtenir la valeur du curseur (10-300)
        slider_value = self.speed_slider.value()
        
        # Convertir en vitesse d'animation en secondes (plus lent = valeur plus élevée)
        # Mapper 10-300 à 2.0-0.1 secondes (inversé)
        self.animation_speed = 2.0 - (slider_value - 10) * (1.9 / 290)
        
        # La vitesse minimale doit être de 0,1 secondes
        self.animation_speed = max(0.1, self.animation_speed)
        
        # Mettre à jour le timer s'il est actif
        if self.animation_timer.isActive():
            self.animation_timer.setInterval(int(self.animation_speed * 1000))
        
    def start_animation(self):
        """Démarrer l'animation"""
        # Désactiver les boutons pendant l'animation
        self.start_btn.setEnabled(False)
        self.step_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        # Définir l'intervalle du timer selon la vitesse
        self.animation_timer.setInterval(int(self.animation_speed * 1000))
        
        # Démarrer le timer pour appeler step_animation périodiquement
        self.animation_timer.start()
        
    def step_animation(self):
        """Avancer d'une étape dans l'algorithme sur les deux graphes"""
        # Variables pour suivre si l'un des graphes a terminé pendant ce tour
        graph1_just_finished = False
        graph2_just_finished = False
        
        # Traitement du graphe 1
        if self.current_edge_index1 < len(self.sorted_edges1):
            # Obtenir l'arête courante
            u, v, w = self.sorted_edges1[self.current_edge_index1]
            current_edge = (u, v, w)
            
            # Mettre à jour les statistiques
            self.stats1["edges_considered"] += 1
            
            # Vérifier si l'ajout de cette arête crée un cycle
            if self.ds1.find(u) != self.ds1.find(v):
                # Pas de cycle - ajouter à l'ACM
                self.ds1.union(u, v)
                self.mst_edges1.append(current_edge)
                self.stats1["edges_accepted"] += 1
            else:
                # Un cycle serait formé - rejeter
                self.stats1["edges_rejected"] += 1
            
            # Mettre à jour la visualisation
            self.graph_view1.draw_graph(self.graph1, self.mst_edges1, current_edge)
            
            # Passer à l'arête suivante
            self.current_edge_index1 += 1
            
            # Vérifier si on vient juste de terminer le premier graphe
            if self.current_edge_index1 >= len(self.sorted_edges1):
                graph1_just_finished = True
                # Mettre à jour l'état final du graphe 1
                self.graph_view1.draw_graph(self.graph1, self.mst_edges1, None)
        
        # Traitement du graphe 2
        if self.current_edge_index2 < len(self.sorted_edges2):
            # Obtenir l'arête courante
            u, v, w = self.sorted_edges2[self.current_edge_index2]
            current_edge = (u, v, w)
            
            # Mettre à jour les statistiques
            self.stats2["edges_considered"] += 1
            
            # Vérifier si l'ajout de cette arête crée un cycle
            if self.ds2.find(u) != self.ds2.find(v):
                # Pas de cycle - ajouter à l'ACM
                self.ds2.union(u, v)
                self.mst_edges2.append(current_edge)
                self.stats2["edges_accepted"] += 1
            else:
                # Un cycle serait formé - rejeter
                self.stats2["edges_rejected"] += 1
            
            # Mettre à jour la visualisation
            self.graph_view2.draw_graph(self.graph2, self.mst_edges2, current_edge)
            
            # Passer à l'arête suivante
            self.current_edge_index2 += 1
            
            # Vérifier si on vient juste de terminer le deuxième graphe
            if self.current_edge_index2 >= len(self.sorted_edges2):
                graph2_just_finished = True
                # Mettre à jour l'état final du graphe 2
                self.graph_view2.draw_graph(self.graph2, self.mst_edges2, None)
        
        # Mettre à jour l'affichage des statistiques pour les deux graphes
        self.update_stats_display()
        
        # Vérifier si les deux algorithmes sont terminés
        if (self.current_edge_index1 >= len(self.sorted_edges1) and 
            self.current_edge_index2 >= len(self.sorted_edges2)):
            # Arrêter le timer si les deux sont terminés
            self.animation_timer.stop()
            self.start_btn.setEnabled(False)
            self.step_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)
            
            # Afficher la comparaison finale
            self.show_final_comparison()
        
        # Mise à jour des insights dans différents scénarios
        if graph1_just_finished or graph2_just_finished:
            # Un des graphes vient juste de terminer, forcer une mise à jour des insights
            self.update_insights(force_update=True)
        elif (self.current_edge_index1 % 5 == 0 or 
            self.current_edge_index2 % 5 == 0):
            # Mise à jour périodique pendant l'exécution
            self.update_insights()
    
    def stop_animation(self):
        """Arrêter l'animation"""
        # Arrêter le timer
        self.animation_timer.stop()
        
        # Réactiver les boutons
        self.start_btn.setEnabled(True)
        self.step_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def reset_animation(self):
        """Réinitialiser l'animation au début"""
        # Arrêter l'animation si elle est en cours
        if self.animation_timer.isActive():
            self.animation_timer.stop()
        
        # Réinitialiser les variables pour le graphe 1
        self.mst_edges1 = []
        self.current_edge_index1 = 0
        self.ds1 = DisjointSet(list(self.graph1.nodes()))
        self.stats1 = {
            "edges_considered": 0,
            "edges_accepted": 0,
            "edges_rejected": 0
        }
        
        # Réinitialiser les variables pour le graphe 2
        self.mst_edges2 = []
        self.current_edge_index2 = 0
        self.ds2 = DisjointSet(list(self.graph2.nodes()))
        self.stats2 = {
            "edges_considered": 0,
            "edges_accepted": 0,
            "edges_rejected": 0
        }
        
        # Mettre à jour les visualisations
        self.graph_view1.draw_graph(self.graph1)
        self.graph_view2.draw_graph(self.graph2)
        
        # Mettre à jour l'affichage des statistiques
        self.update_stats_display()
        
        # Réinitialiser le texte des insights
        self.insights_text.setHtml("<h3>Exécutez l'algorithme pour voir l'analyse détaillée</h3>")
        
        # Activer les boutons démarrer/étape
        self.start_btn.setEnabled(True)
        self.step_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
    
    def update_insights(self, force_update=False):
        """Générer des analyses en temps réel pendant l'exécution de l'algorithme"""
        insights = []
        
        # Obtenir la progression de l'algorithme
        progress1 = self.current_edge_index1 / len(self.sorted_edges1) if self.sorted_edges1 else 0
        progress2 = self.current_edge_index2 / len(self.sorted_edges2) if self.sorted_edges2 else 0
        
        # Ajouter l'en-tête sur l'algorithme de Kruskal - TOUJOURS AFFICHER
        insights.append("📚 L'ALGORITHME DE KRUSKAL")
        insights.append("=" * 30)
        insights.append("L'algorithme de Kruskal construit un Arbre Couvrant Minimal (ACM) en")
        insights.append("traitant les arêtes par ordre croissant de poids et en évitant les cycles.")
        insights.append("C'est un algorithme glouton qui garantit une solution optimale.")
        insights.append("\nObservez l'évolution de l'algorithme et attendez la fin pour")
        insights.append("des explications détaillées sur cette comparaison spécifique.")
        
        # Toujours ajouter les informations de progression
        insights.append("\n• Progression:")
        
        if self.current_edge_index1 >= len(self.sorted_edges1):
            insights.append(f"  Graphe 1: 100% - TERMINÉ ✅")
        else:
            insights.append(f"  Graphe 1: {progress1*100:.0f}% ({self.current_edge_index1}/{len(self.sorted_edges1)})")
            
        if self.current_edge_index2 >= len(self.sorted_edges2):
            insights.append(f"  Graphe 2: 100% - TERMINÉ ✅")
        else:
            insights.append(f"  Graphe 2: {progress2*100:.0f}% ({self.current_edge_index2}/{len(self.sorted_edges2)})")
        
        # Toujours afficher la section des arêtes ACM
        insights.append("\n• Arêtes ACM trouvées:")
        insights.append(f"  Graphe 1: {len(self.mst_edges1)} arêtes")
        insights.append(f"  Graphe 2: {len(self.mst_edges2)} arêtes")
        
        # Mettre à jour le texte des insights avec un espacement approprié
        # Utiliser setHtml pour préserver la mise en forme
        html_content = "<br>".join(insights).replace("\n", "<br>")
        self.insights_text.setHtml(html_content)
    
    def _count_current_components(self, graph, mst_edges):
        """Méthode auxiliaire pour compter les composantes connexes dans l'état actuel de l'ACM"""
        # Créer un graphe avec uniquement les arêtes de l'ACM
        g = nx.Graph()
        g.add_nodes_from(graph.nodes())
        g.add_edges_from([(u, v) for u, v, _ in mst_edges])
    
    def show_final_comparison(self):
        """Afficher la comparaison finale et les insights éducatifs"""
        print("Fonction show_final_comparison() appelée") # Message de débogage
        
        # Forçons un message pour indiquer que les insights sont en cours de chargement
        self.insights_text.setHtml("<h3 style='color:blue'>Préparation de l'analyse finale... veuillez patienter</h3>")
        
        # Petit délai pour s'assurer que l'interface se met à jour
        QTimer.singleShot(100, self._do_show_final_comparison)
        
    def _do_show_final_comparison(self):
        """Implémentation réelle de l'affichage des insights finaux après un court délai"""
        print("Chargement des insights finaux") # Message de débogage
        final_insights = []
        
        # Effacer la ligne pointillée en redessinant sans current_edge
        self.graph_view1.draw_graph(self.graph1, self.mst_edges1, None)
        self.graph_view2.draw_graph(self.graph2, self.mst_edges2, None)
        
        # Comparer les propriétés des ACM
        if self.mst_edges1 and self.mst_edges2:
            # Calculer les statistiques clés
            mst_weight1 = sum(w for _, _, w in self.mst_edges1)
            mst_weight2 = sum(w for _, _, w in self.mst_edges2)
            
            # Créer des objets graphe à partir des ACM pour analyser leurs propriétés
            G1 = nx.Graph()
            G1.add_nodes_from(self.graph1.nodes())
            G1.add_edges_from([(u, v) for u, v, _ in self.mst_edges1])
            
            G2 = nx.Graph()
            G2.add_nodes_from(self.graph2.nodes())
            G2.add_edges_from([(u, v) for u, v, _ in self.mst_edges2])
            
            comp1 = nx.number_connected_components(G1)
            comp2 = nx.number_connected_components(G2)
            
            # Ajouter le titre et le résumé
            final_insights.append(f"📊 Comparaison des ACM: {self.graph1_name} vs {self.graph2_name}")
            final_insights.append("=" * 60)
            
            # Utiliser directement le nom de la catégorie au lieu d'essayer de le détecter à partir des noms de graphes
            if self.category_name == "Connexe vs Déconnecté":
                final_insights.append("\n🔍 ANALYSE: Graphes Connexes vs Déconnectés")
                final_insights.append("---------------------------------------------------")
                
                # Identifier quel graphe est lequel
                connected_graph = "Graphe 1" if comp1 == 1 else "Graphe 2" 
                disconnected_graph = "Graphe 2" if comp1 == 1 else "Graphe 1"
                connected_idx = 0 if connected_graph == "Graphe 1" else 1
                disconnected_idx = 1 if connected_graph == "Graphe 1" else 0
                
                # Calculer les compteurs pour chaque graphe
                conn_edges = len(self.mst_edges1 if connected_idx == 0 else self.mst_edges2)
                disconn_edges = len(self.mst_edges2 if connected_idx == 0 else self.mst_edges1)
                disconn_comp = comp2 if disconnected_graph == "Graphe 2" else comp1
                
                # Ajouter des observations claires
                final_insights.append(f"• {connected_graph} a produit un véritable ACM (1 composante connexe)")
                final_insights.append(f"• {disconnected_graph} a produit une FCM avec {disconn_comp} arbres séparés")
                
                # Ajouter des explications éducatives
                final_insights.append("\nPoints Clés:")
                final_insights.append("1. Quand un graphe a des composantes déconnectées, l'algorithme de Kruskal crée")
                final_insights.append("   des arbres optimaux dans chaque composante mais ne peut pas les connecter.")
                final_insights.append(f"2. La FCM du {disconnected_graph} a exactement {disconn_comp} arbres car")
                final_insights.append("   le graphe original avait exactement ce nombre de composantes déconnectées.")
                final_insights.append("3. L'ACM/FCM aura exactement (n-c) arêtes, où n est le nombre de")
                final_insights.append("   sommets et c est le nombre de composantes connexes.")
                final_insights.append("4. Ceci illustre que l'algorithme de Kruskal opère globalement sur toutes")
                final_insights.append("   les composantes simultanément, sans partir d'un sommet spécifique.")
                
            elif self.category_name == "Dense vs Clairsemé":
                final_insights.append("\n🔍 ANALYSE: Graphes Denses vs Clairsemés")
                final_insights.append("------------------------------------------")
                
                # Identifier quel graphe est lequel
                edges1 = self.graph1.number_of_edges()
                edges2 = self.graph2.number_of_edges()
                dense_graph = "Graphe 1" if edges1 > edges2 else "Graphe 2"
                sparse_graph = "Graphe 2" if edges1 > edges2 else "Graphe 1"
                dense_idx = 0 if dense_graph == "Graphe 1" else 1
                sparse_idx = 1 if dense_graph == "Graphe 1" else 0
                
                # Calculer les statistiques
                dense_stats = self.stats1 if dense_idx == 0 else self.stats2
                sparse_stats = self.stats2 if dense_idx == 0 else self.stats1
                dense_reject_rate = dense_stats["edges_rejected"] / dense_stats["edges_considered"] * 100
                sparse_reject_rate = sparse_stats["edges_rejected"] / sparse_stats["edges_considered"] * 100
                
                # Ajouter des observations claires
                final_insights.append(f"• {dense_graph}: {max(edges1, edges2)} arêtes, rejet de {dense_reject_rate:.1f}% des arêtes considérées")
                final_insights.append(f"• {sparse_graph}: {min(edges1, edges2)} arêtes, rejet de {sparse_reject_rate:.1f}% des arêtes considérées")
                
                # Ajouter des explications éducatives
                final_insights.append("\nPoints Clés:")
                final_insights.append("1. Les graphes denses nécessitent significativement plus de vérifications de cycles")
                final_insights.append("   pendant l'exécution de l'algorithme, rendant le taux de rejet beaucoup plus élevé.")
                final_insights.append(f"2. Le {dense_graph} a dû considérer beaucoup plus d'arêtes possibles, mais")
                final_insights.append("   s'est tout de même retrouvé avec un nombre d'arêtes ACM similaire au graphe clairsemé.")
                final_insights.append("3. Impact sur la complexité temporelle: Dans les graphes denses, l'efficacité")
                final_insights.append("   de la structure Union-Find devient critique pour la performance.")
                final_insights.append("4. Cela démontre que la taille de l'ACM dépend uniquement du nombre de sommets,")
                final_insights.append("   pas du nombre initial d'arêtes du graphe.")
                
            elif self.category_name == "ACM Unique vs ACM Multiples":
                final_insights.append("\n🔍 ANALYSE: ACM Unique vs ACM Multiples Possibles")
                final_insights.append("--------------------------------------------------------")
                
                # Ajouter des observations claires avec explications éducatives
                final_insights.append("• Les poids d'arêtes uniques garantissent exactement une seule solution d'ACM possible")
                final_insights.append("• Les poids d'arêtes identiques peuvent conduire à plusieurs configurations valides d'ACM")
                
                # Ajouter des explications éducatives
                final_insights.append("\nPoints Clés:")
                final_insights.append("1. Quand les poids des arêtes sont uniques, l'algorithme de Kruskal produit le même ACM")
                final_insights.append("   indépendamment des détails d'implémentation ou de l'ordre de traitement des arêtes.")
                final_insights.append("2. Avec des poids dupliqués, l'ACM spécifique trouvé dépend de l'ordre dans")
                final_insights.append("   lequel les arêtes de poids égal sont traitées.")
                final_insights.append("3. Tous les ACM valides auront le même poids total, quel que soit le choix")
                final_insights.append("   spécifique des arêtes de poids égal.")
                final_insights.append("4. Application réelle: Les concepteurs de réseaux peuvent choisir parmi plusieurs")
                final_insights.append("   ACM optimaux ayant des propriétés différentes mais des coûts totaux égaux.")
                
            elif self.category_name == "Distributions des Poids d'Arêtes":
                final_insights.append("\n🔍 ANALYSE: Distributions des Poids d'Arêtes")
                final_insights.append("----------------------------------------------------")
                
                # Calculer les statistiques de poids
                weights1 = [w for _, _, w in self.sorted_edges1]
                weights2 = [w for _, _, w in self.sorted_edges2]
                avg1 = sum(weights1) / len(weights1) if weights1 else 0
                avg2 = sum(weights2) / len(weights2) if weights2 else 0
                
                # Ajouter des observations claires
                final_insights.append(f"• Graphe 1: Poids moyen des arêtes {avg1:.2f}, poids de l'ACM {mst_weight1:.2f}")
                final_insights.append(f"• Graphe 2: Poids moyen des arêtes {avg2:.2f}, poids de l'ACM {mst_weight2:.2f}")
                
                # Ajouter des explications éducatives
                final_insights.append("\nPoints Clés:")
                final_insights.append("1. L'algorithme de Kruskal est entièrement guidé par les poids - la séquence")
                final_insights.append("   de sélection des arêtes est déterminée uniquement par les valeurs de poids.")
                final_insights.append("2. La distribution des poids des arêtes affecte l'ordre de traitement,")
                final_insights.append("   mais l'algorithme trouve toujours la solution globalement optimale.")
                final_insights.append("3. L'ACM tend à préférer les arêtes de poids faible indépendamment de leur")
                final_insights.append("   position dans la structure du graphe.")
                final_insights.append("4. Cela démontre la robustesse de l'approche gloutonne quand le problème")
                final_insights.append("   possède une sous-structure optimale et la propriété de choix glouton.")
                
            elif self.category_name == "Propriétés Structurelles Différentes":
                final_insights.append("\n🔍 ANALYSE: Propriétés Structurelles Différentes")
                final_insights.append("------------------------------------------------")
                
                # Calculer les statistiques structurelles
                avg_deg1 = 2 * self.graph1.number_of_edges() / self.graph1.number_of_nodes()
                avg_deg2 = 2 * self.graph2.number_of_edges() / self.graph2.number_of_nodes()
                
                # Ajouter des observations claires
                final_insights.append(f"• Graphe 1: Degré moyen {avg_deg1:.1f}, crée un ACM avec {len(self.mst_edges1)} arêtes")
                final_insights.append(f"• Graphe 2: Degré moyen {avg_deg2:.1f}, crée un ACM avec {len(self.mst_edges2)} arêtes")
                
                # Ajouter des explications éducatives
                final_insights.append("\nPoints Clés:")
                final_insights.append("1. Différentes structures de graphes créent différents patterns de formation de cycles,")
                final_insights.append("   mais l'algorithme trouve toujours l'arbre couvrant optimal.")
                final_insights.append("2. Les clusters denses dans le graphe conduisent à plus de détections de cycles")
                final_insights.append("   et de rejets d'arêtes pendant l'exécution de l'algorithme.")
                final_insights.append("3. L'ACM préserve la connectivité du graphe tout en supprimant tous")
                final_insights.append("   les chemins redondants et en minimisant le poids total.")
                final_insights.append("4. D'une perspective théorique, l'ACM représente la façon la plus économique")
                final_insights.append("   de connecter tous les sommets avec le poids total minimum possible.")
            
            # Ajouter la comparaison statistique
            final_insights.append("\n📈 Comparaison Statistique")
            final_insights.append("-------------------------")
            
            # Comparaison des propriétés de base
            final_insights.append(f"• Graphe 1: {self.graph1.number_of_nodes()} sommets, {self.graph1.number_of_edges()} arêtes")
            final_insights.append(f"• Graphe 2: {self.graph2.number_of_nodes()} sommets, {self.graph2.number_of_edges()} arêtes")
            
            # Comparaison des résultats des ACM
            final_insights.append(f"\nRésultats des ACM:")
            final_insights.append(f"• Graphe 1: {len(self.mst_edges1)} arêtes dans l'ACM, poids total {mst_weight1:.2f}")
            final_insights.append(f"• Graphe 2: {len(self.mst_edges2)} arêtes dans l'ACM, poids total {mst_weight2:.2f}")
            
            # Comparaison des performances
            accept_rate1 = self.stats1["edges_accepted"] / self.stats1["edges_considered"] * 100
            accept_rate2 = self.stats2["edges_accepted"] / self.stats2["edges_considered"] * 100
            final_insights.append(f"\nPerformance de l'Algorithme:")
            final_insights.append(f"• Graphe 1: {accept_rate1:.1f}% taux d'acceptation d'arêtes")
            final_insights.append(f"• Graphe 2: {accept_rate2:.1f}% taux d'acceptation d'arêtes")
            
            # Information sur la connectivité
            if comp1 > 1 or comp2 > 1:
                final_insights.append(f"\nConnectivité:")
                if comp1 > 1:
                    final_insights.append(f"• Graphe 1 a produit une forêt avec {comp1} arbres")
                if comp2 > 1:
                    final_insights.append(f"• Graphe 2 a produit une forêt avec {comp2} arbres")
            
            # Ajouter la conclusion avec les principes fondamentaux démontrés
            final_insights.append("\n📝 PRINCIPES FONDAMENTAUX")
            final_insights.append("=" * 25)
            final_insights.append("L'algorithme de Kruskal démontre ces principes clés:")
            final_insights.append("1. Choix Glouton: Sélectionne toujours les arêtes de poids minimal en premier")
            final_insights.append("2. Évitement de Cycles: Rejette efficacement les arêtes qui créeraient des cycles")
            final_insights.append("3. Solution Optimale: Produit un arbre/forêt couvrant(e) de poids minimum")
            final_insights.append("4. Gestion des Composantes: Traite naturellement les graphes déconnectés")
            final_insights.append("5. Priorisation des Arêtes: Ordonne les arêtes strictement par poids, non par position")
            
            # Ajouter des insights spécifiques basés sur la paire de graphes comparée
            graph_categories = [
                ("Dense vs Clairsemé", "DENSITÉ ET PERFORMANCE", [
                    "La densité du graphe affecte considérablement le taux de rejet d'arêtes.",
                    "Plus un graphe est dense, plus la structure Union-Find devient critique.",
                    "Un graphe dense avec n sommets aura O(n²) arêtes mais seulement (n-1) dans son ACM.",
                    "La complexité O(m log m) de Kruskal est dominée par le tri des arêtes."
                ]),
                ("Connexe vs Déconnecté", "CONNECTIVITÉ ET FORÊTS", [
                    "Contrairement à Prim, Kruskal n'a pas besoin d'un point de départ spécifique.",
                    "Sur un graphe déconnecté, Kruskal produit une Forêt Couvrante Minimale (FCM).",
                    "Le nombre d'arêtes de la FCM est exactement (n-c) où c est le nombre de composantes.",
                    "Cette propriété illustre la flexibilité de Kruskal face aux structures variées."
                ]),
                ("ACM Unique vs ACM Multiples", "UNICITÉ DES SOLUTIONS", [
                    "Un graphe possède un unique ACM si et seulement si tous ses poids d'arêtes sont distincts.",
                    "Avec des poids dupliqués, différentes exécutions peuvent produire des ACM différents.",
                    "Tous les ACM valides ont exactement le même poids total.",
                    "L'indéterminisme offre une flexibilité pratique dans les applications réelles."
                ]),
                ("Distributions des Poids", "INFLUENCE DES POIDS", [
                    "Kruskal fonctionne même avec des poids négatifs, contrairement à d'autres algorithmes.",
                    "La distribution des poids impacte uniquement l'ordre de traitement, pas le résultat final.",
                    "C'est la preuve d'un algorithme glouton où les choix locaux optimaux mènent à un optimum global.",
                    "Cette propriété est garantie par la matroïde sous-jacente au problème de l'ACM."
                ]),
                ("Propriétés Structurelles", "TOPOLOGIE ET PATTERNS", [
                    "Différentes structures de graphes produisent des motifs d'ACM caractéristiques.",
                    "Les grilles tendent à former des 'rivières', les graphes aléatoires des arbres irréguliers.",
                    "Malgré ces différences, les propriétés mathématiques de l'ACM restent constantes.",
                    "Kruskal démontre l'invariance du théorème fondamental de caractérisation des arbres."
                ])
            ]
            
            # Trouver la catégorie que nous montrons
            found_category = False
            for category_name, title, insights_list in graph_categories:
                if category_name in self.graph1_name + self.graph2_name:
                    final_insights.append(f"\n📊 {title}")
                    final_insights.append("=" * 25)
                    for insight in insights_list:
                        final_insights.append(f"• {insight}")
                    found_category = True
                    break
            
            # Si aucune catégorie n'est trouvée, ajouter un message pour le débogage
            if not found_category:
                print(f"Aucune catégorie trouvée pour: {self.graph1_name} + {self.graph2_name}")
                
        # Mettre à jour le texte des insights avec l'analyse finale
        # Utiliser setHtml pour préserver la mise en forme avec un style amélioré
        html_content = "<div style='font-size: 14px; line-height: 1.5;'>" + "<br>".join(final_insights).replace("\n", "<br>") + "</div>"
        self.insights_text.setHtml(html_content)
        print(f"Insights finaux affichés avec {len(final_insights)} lignes")