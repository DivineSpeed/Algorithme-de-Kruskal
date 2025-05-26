from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                         QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                         QGroupBox, QSpinBox, QDoubleSpinBox, QHeaderView, QSplitter,
                         QFrame, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt
import networkx as nx
import random
import numpy as np
from visualisation_graphe import CytoscapeGraphView

class GraphDrawingArea(QFrame):
    """Widget pour visualiser le graphe pendant sa création"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 300)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Sunken)
        
        # Initialiser la visualisation du graphe
        layout = QVBoxLayout(self)
        self.graph_view = CytoscapeGraphView()
        layout.addWidget(self.graph_view)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Initialiser un graphe vide
        self.graph = nx.Graph()
        
    def update_graph(self, nodes, edges):
        """Mettre à jour la visualisation du graphe avec les nouveaux sommets et arêtes"""
        self.graph = nx.Graph()
        
        # Ajouter les sommets
        for node_id in nodes:
            self.graph.add_node(node_id)
            
        # Ajouter les arêtes
        for edge in edges:
            if len(edge) >= 3:  # S'assurer qu'on a source, destination, poids
                self.graph.add_edge(edge[0], edge[1], weight=edge[2])
        
        # Redessiner si nous avons des sommets (éviter l'erreur "graphe nul")
        if nodes:
            self.graph_view.draw_graph(self.graph)
        else:
            # Réinitialiser la vue quand il n'y a pas de sommets
            self.graph_view.reset_view()


class CustomGraphDialog(QDialog):
    """Boîte de dialogue pour créer des graphes personnalisés"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Créer un Graphe Personnalisé")
        self.resize(900, 700)  # Taille plus grande pour une meilleure édition de graphe
        
        # Initialiser les données du graphe
        self.nodes = []
        self.edges = []
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        
        # Create a splitter for left panel (controls) and right panel (visualization)
        splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Controls
        left_panel = QFrame()
        left_layout = QVBoxLayout(left_panel)
        
        # Node controls
        node_group = QGroupBox("Sommets")
        node_layout = QVBoxLayout()
        
        # Node creation
        node_add_layout = QHBoxLayout()
        self.node_id_input = QLineEdit()
        self.node_id_input.setPlaceholderText("ID du sommet (ex: A, B, 1, 2...)")
        node_add_btn = QPushButton("Ajouter Sommet")
        node_add_btn.clicked.connect(self.add_node)
        node_add_layout.addWidget(self.node_id_input)
        node_add_layout.addWidget(node_add_btn)
        node_layout.addLayout(node_add_layout)
        
        # Node list
        self.node_table = QTableWidget(0, 2)  # id, delete button
        self.node_table.setHorizontalHeaderLabels(["ID du Sommet", "Actions"])
        self.node_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.node_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.node_table.setColumnWidth(1, 100)
        node_layout.addWidget(self.node_table)
        
        # Quick node generation
        quick_node_layout = QHBoxLayout()
        quick_node_layout.addWidget(QLabel("Ajout rapide:"))
        self.num_nodes_spinbox = QSpinBox()
        self.num_nodes_spinbox.setRange(1, 50)
        self.num_nodes_spinbox.setValue(5)
        quick_node_layout.addWidget(self.num_nodes_spinbox)
        quick_add_btn = QPushButton("Générer Sommets")
        quick_add_btn.clicked.connect(self.generate_nodes)
        quick_node_layout.addWidget(quick_add_btn)
        node_layout.addLayout(quick_node_layout)
        
        node_group.setLayout(node_layout)
        left_layout.addWidget(node_group)
        
        # Edge controls
        edge_group = QGroupBox("Arêtes")
        edge_layout = QVBoxLayout()
        
        # Edge creation
        edge_add_layout = QHBoxLayout()
        self.edge_source = QComboBox()
        self.edge_source.setPlaceholderText("Source")
        self.edge_target = QComboBox()
        self.edge_target.setPlaceholderText("Destination")
        self.edge_weight = QDoubleSpinBox()
        self.edge_weight.setRange(0.1, 100.0)
        self.edge_weight.setValue(1.0)
        self.edge_weight.setSingleStep(0.1)
        edge_add_btn = QPushButton("Ajouter Arête")
        edge_add_btn.clicked.connect(self.add_edge)
        
        edge_add_layout.addWidget(QLabel("De:"))
        edge_add_layout.addWidget(self.edge_source)
        edge_add_layout.addWidget(QLabel("Vers:"))
        edge_add_layout.addWidget(self.edge_target)
        edge_add_layout.addWidget(QLabel("Poids:"))
        edge_add_layout.addWidget(self.edge_weight)
        edge_add_layout.addWidget(edge_add_btn)
        edge_layout.addLayout(edge_add_layout)
        
        # Edge list
        self.edge_table = QTableWidget(0, 4)  # source, target, weight, delete
        self.edge_table.setHorizontalHeaderLabels(["Source", "Destination", "Poids", "Actions"])
        self.edge_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.edge_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.edge_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.edge_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.edge_table.setColumnWidth(3, 100)
        edge_layout.addWidget(self.edge_table)
        
        # Quick edge generation
        quick_edge_layout = QHBoxLayout()
        quick_edge_layout.addWidget(QLabel("Générer Arêtes:"))
        self.edge_type = QComboBox()
        self.edge_type.addItems(["Arêtes Aléatoires", "Graphe Complet", "Arbre Couvrant Minimal", "Cycle/Anneau"])
        quick_edge_layout.addWidget(self.edge_type)
        
        edge_density_layout = QHBoxLayout()
        edge_density_layout.addWidget(QLabel("Densité d'Arêtes:"))
        self.edge_density = QDoubleSpinBox()
        self.edge_density.setRange(0.1, 1.0)
        self.edge_density.setValue(0.3)
        self.edge_density.setSingleStep(0.1)
        edge_density_layout.addWidget(self.edge_density)
        
        quick_edge_btn = QPushButton("Générer Arêtes")
        quick_edge_btn.clicked.connect(self.generate_edges)
        
        edge_gen_layout = QVBoxLayout()
        edge_gen_layout.addLayout(quick_edge_layout)
        edge_gen_layout.addLayout(edge_density_layout)
        edge_gen_layout.addWidget(quick_edge_btn)
        
        edge_layout.addLayout(edge_gen_layout)
        edge_group.setLayout(edge_layout)
        left_layout.addWidget(edge_group)
        
        # Create a preview/finalize section at the bottom
        preview_layout = QHBoxLayout()
        
        # Random weights option
        self.randomize_weights = QCheckBox("Poids Aléatoires")
        self.randomize_weights.setChecked(False)
        
        # Graph name
        graph_name_layout = QHBoxLayout()
        graph_name_layout.addWidget(QLabel("Nom du Graphe:"))
        self.graph_name = QLineEdit()
        self.graph_name.setPlaceholderText("Mon Graphe Personnalisé")
        self.graph_name.setText("Graphe Personnalisé")
        graph_name_layout.addWidget(self.graph_name)
        
        preview_layout.addWidget(self.randomize_weights)
        preview_layout.addLayout(graph_name_layout)
        left_layout.addLayout(preview_layout)
        
        # Right panel - Graph visualization
        self.graph_drawing = GraphDrawingArea()
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(self.graph_drawing)
        splitter.setSizes([300, 600])  # Initial sizes
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        create_btn = QPushButton("Créer Graphe")
        create_btn.clicked.connect(self.create_graph)
        cancel_btn = QPushButton("Annuler")
        cancel_btn.clicked.connect(self.reject)
        clear_btn = QPushButton("Tout Effacer")
        clear_btn.clicked.connect(self.clear_all)
        
        button_layout.addWidget(clear_btn)
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(create_btn)
        
        main_layout.addLayout(button_layout)
        
    def add_node(self):
        """Ajouter un nouveau sommet au graphe"""
        node_id = self.node_id_input.text().strip()
        
        if not node_id:
            QMessageBox.warning(self, "Erreur de Saisie", "Veuillez entrer un ID de sommet")
            return
        
        if node_id in self.nodes:
            QMessageBox.warning(self, "Sommet en Double", f"Le sommet '{node_id}' existe déjà")
            return
        
        # Ajouter à la liste interne
        self.nodes.append(node_id)
        
        # Ajouter au tableau
        row = self.node_table.rowCount()
        self.node_table.insertRow(row)
        self.node_table.setItem(row, 0, QTableWidgetItem(node_id))
        
        # Ajouter un bouton de suppression
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(lambda: self.delete_node(node_id))
        self.node_table.setCellWidget(row, 1, delete_btn)
        
        # Mettre à jour les listes déroulantes
        self.update_node_comboboxes()
        
        # Effacer le champ de saisie
        self.node_id_input.clear()
        
        # Mettre à jour la visualisation
        self.update_graph_view()
    
    def delete_node(self, node_id):
        """Supprimer un sommet et toutes ses arêtes connectées"""
        if node_id in self.nodes:
            # Supprimer de la liste des sommets
            self.nodes.remove(node_id)
            
            # Supprimer toutes les arêtes connectées à ce sommet
            self.edges = [edge for edge in self.edges if edge[0] != node_id and edge[1] != node_id]
            
            # Mettre à jour les tableaux
            self.update_tables()
            
            # Mettre à jour les listes déroulantes
            self.update_node_comboboxes()
            
            # Mettre à jour la visualisation
            self.update_graph_view()
    
    def generate_nodes(self):
        """Générer automatiquement un nombre spécifié de sommets"""
        num_nodes = self.num_nodes_spinbox.value()
        
        # Générer des noms de sommets en fonction de ce qui existe déjà
        existing_numeric = [n for n in self.nodes if n.isdigit()]
        existing_alpha = [n for n in self.nodes if n.isalpha()]
        
        new_nodes = []
        if len(existing_alpha) <= len(existing_numeric):
            # Générer des identifiants alphabétiques
            start_char = ord('A')
            for i in range(num_nodes):
                node_id = chr(start_char + i)
                while node_id in self.nodes:
                    start_char += 1
                    node_id = chr(start_char)
                new_nodes.append(node_id)
        else:
            # Générer des identifiants numériques
            start_num = 1
            for i in range(num_nodes):
                node_id = str(start_num + i)
                while node_id in self.nodes:
                    start_num += 1
                    node_id = str(start_num)
                new_nodes.append(node_id)
        
        # Ajouter tous les nouveaux sommets
        for node_id in new_nodes:
            self.nodes.append(node_id)
        
        # Mettre à jour les tableaux
        self.update_tables()
        
        # Mettre à jour les listes déroulantes
        self.update_node_comboboxes()
        
        # Mettre à jour la visualisation
        self.update_graph_view()
    
    def add_edge(self):
        """Ajouter une nouvelle arête au graphe"""
        source = self.edge_source.currentText()
        target = self.edge_target.currentText()
        weight = self.edge_weight.value()
        
        if source == target:
            QMessageBox.warning(self, "Arête Invalide", "Les boucles sur un même sommet ne sont pas autorisées")
            return
        
        # Vérifier si l'arête existe déjà
        for edge in self.edges:
            if (edge[0] == source and edge[1] == target) or (edge[0] == target and edge[1] == source):
                QMessageBox.warning(self, "Arête en Double", f"Une arête entre {source} et {target} existe déjà")
                return
        
        # Ajouter à la liste interne
        self.edges.append((source, target, weight))
        
        # Ajouter au tableau
        row = self.edge_table.rowCount()
        self.edge_table.insertRow(row)
        self.edge_table.setItem(row, 0, QTableWidgetItem(source))
        self.edge_table.setItem(row, 1, QTableWidgetItem(target))
        self.edge_table.setItem(row, 2, QTableWidgetItem(str(weight)))
        
        # Ajouter un bouton de suppression
        delete_btn = QPushButton("Supprimer")
        delete_btn.clicked.connect(lambda: self.delete_edge(row))
        self.edge_table.setCellWidget(row, 3, delete_btn)
        
        # Mettre à jour la visualisation
        self.update_graph_view()
    
    def delete_edge(self, row):
        """Supprimer une arête en fonction de sa ligne dans le tableau"""
        if 0 <= row < len(self.edges):
            # Supprimer de la liste des arêtes
            del self.edges[row]
            
            # Mettre à jour les tableaux
            self.update_tables()
            
            # Mettre à jour la visualisation
            self.update_graph_view()
    
    def generate_edges(self):
        """Générer des arêtes selon le modèle sélectionné"""
        if len(self.nodes) < 2:
            QMessageBox.warning(self, "Pas Assez de Sommets", "Au moins 2 sommets sont requis pour créer des arêtes")
            return
        
        # Effacer les arêtes existantes
        self.edges = []
        
        edge_type = self.edge_type.currentText()
        
        if edge_type == "Graphe Complet":
            # Créer des arêtes entre toutes les paires de sommets
            for i in range(len(self.nodes)):
                for j in range(i + 1, len(self.nodes)):
                    weight = round(random.uniform(1, 10), 1)
                    self.edges.append((self.nodes[i], self.nodes[j], weight))
                    
        elif edge_type == "Arêtes Aléatoires":
            # Créer des arêtes aléatoires selon la densité
            density = self.edge_density.value()
            max_edges = len(self.nodes) * (len(self.nodes) - 1) // 2
            num_edges = int(max_edges * density)
            
            # Créer une liste de toutes les arêtes possibles
            possible_edges = []
            for i in range(len(self.nodes)):
                for j in range(i + 1, len(self.nodes)):
                    possible_edges.append((self.nodes[i], self.nodes[j]))
            
            # Sélectionner des arêtes aléatoirement
            selected_edges = random.sample(possible_edges, min(num_edges, len(possible_edges)))
            
            # Ajouter des poids
            for edge in selected_edges:
                weight = round(random.uniform(1, 10), 1)
                self.edges.append((edge[0], edge[1], weight))
                
        elif edge_type == "Arbre Couvrant Minimal":
            # Créer un graphe acyclique connexe (un arbre)
            # D'abord créer une liste de tous les sommets
            remaining_nodes = self.nodes[1:]
            connected_nodes = [self.nodes[0]]
            
            # Connecter chaque sommet restant à un sommet aléatoire déjà dans l'arbre
            for node in remaining_nodes:
                connect_to = random.choice(connected_nodes)
                weight = round(random.uniform(1, 10), 1)
                self.edges.append((node, connect_to, weight))
                connected_nodes.append(node)
                
        elif edge_type == "Cycle/Anneau":
            # Créer une connexion circulaire
            for i in range(len(self.nodes)):
                next_idx = (i + 1) % len(self.nodes)
                weight = round(random.uniform(1, 10), 1)
                self.edges.append((self.nodes[i], self.nodes[next_idx], weight))
        
        # Mettre à jour le tableau des arêtes
        self.update_tables()
        
        # Mettre à jour la visualisation
        self.update_graph_view()
    
    def update_tables(self):
        """Mettre à jour complètement les tableaux de sommets et d'arêtes"""
        # Effacer et mettre à jour le tableau des sommets
        self.node_table.setRowCount(0)
        for node_id in self.nodes:
            row = self.node_table.rowCount()
            self.node_table.insertRow(row)
            self.node_table.setItem(row, 0, QTableWidgetItem(node_id))
            
            # Ajouter un bouton de suppression
            delete_btn = QPushButton("Supprimer")
            delete_btn.clicked.connect(lambda checked, n=node_id: self.delete_node(n))
            self.node_table.setCellWidget(row, 1, delete_btn)
        
        # Effacer et mettre à jour le tableau des arêtes
        self.edge_table.setRowCount(0)
        for i, (source, target, weight) in enumerate(self.edges):
            row = self.edge_table.rowCount()
            self.edge_table.insertRow(row)
            self.edge_table.setItem(row, 0, QTableWidgetItem(source))
            self.edge_table.setItem(row, 1, QTableWidgetItem(target))
            self.edge_table.setItem(row, 2, QTableWidgetItem(str(weight)))
            
            # Ajouter un bouton de suppression
            delete_btn = QPushButton("Supprimer")
            delete_btn.clicked.connect(lambda checked, r=i: self.delete_edge(r))
            self.edge_table.setCellWidget(row, 3, delete_btn)
    
    def update_node_comboboxes(self):
        """Mettre à jour les listes déroulantes de sélection des sommets"""
        # Stocker les sélections actuelles
        current_source = self.edge_source.currentText()
        current_target = self.edge_target.currentText()
        
        # Effacer et repeupler
        self.edge_source.clear()
        self.edge_target.clear()
        
        self.edge_source.addItems(self.nodes)
        self.edge_target.addItems(self.nodes)
        
        # Restaurer les sélections si possible
        source_idx = self.edge_source.findText(current_source)
        if source_idx >= 0:
            self.edge_source.setCurrentIndex(source_idx)
        
        target_idx = self.edge_target.findText(current_target)
        if target_idx >= 0:
            self.edge_target.setCurrentIndex(target_idx)
    
    def update_graph_view(self):
        """Mettre à jour la visualisation du graphe"""
        self.graph_drawing.update_graph(self.nodes, self.edges)
    
    def clear_all(self):
        """Effacer tous les sommets et arêtes"""
        if self.nodes or self.edges:
            reply = QMessageBox.question(self, "Confirmer l'Effacement", 
                                         "Êtes-vous sûr de vouloir effacer tous les sommets et arêtes?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.nodes = []
                self.edges = []
                self.update_tables()
                self.update_node_comboboxes()
                self.update_graph_view()
    
    def create_graph(self):
        """Créer et retourner le graphe final"""
        if not self.nodes:
            QMessageBox.warning(self, "Graphe Vide", "Veuillez ajouter au moins un sommet")
            return
        
        # Construire le graphe NetworkX
        graph = nx.Graph()
        
        # Ajouter les sommets
        for node_id in self.nodes:
            graph.add_node(node_id)
        
        # Ajouter les arêtes
        for source, target, weight in self.edges:
            # Si l'option de poids aléatoires est cochée, remplacer les poids
            if self.randomize_weights.isChecked():
                weight = round(random.uniform(1, 10), 1)
            graph.add_edge(source, target, weight=weight)
        
        # Valider le graphe
        if not self.validate_graph(graph):
            return
        
        # Retourner le graphe
        self.graph = graph
        self.graph_name_value = self.graph_name.text() or "Graphe Personnalisé"
        self.accept()
    
    def validate_graph(self, graph):
        """Valider le graphe avant de le retourner"""
        # Vérifier si le graphe a des sommets
        if graph.number_of_nodes() == 0:
            QMessageBox.warning(self, "Graphe Invalide", "Le graphe doit avoir au moins un sommet")
            return False
        
        # Avertir des graphes déconnectés
        if not nx.is_connected(graph) and graph.number_of_nodes() > 1:
            reply = QMessageBox.question(self, "Graphe Déconnecté", 
                                         "Votre graphe a des composantes déconnectées. Cela donnera une forêt plutôt qu'un arbre. Continuer quand même?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return False
        
        return True
    
    def get_graph(self):
        """Retourner le graphe créé"""
        return getattr(self, 'graph', None), getattr(self, 'graph_name_value', "Graphe Personnalisé") 