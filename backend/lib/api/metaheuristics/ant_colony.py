"""
Ant Colony Optimization (ACO) implementation for legal document path construction.
This module provides an ACO-based approach to find optimal paths through document sections
for extractive summarization and citation network analysis.
"""

import numpy as np
from typing import List, Dict, Tuple, Any
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

class DocumentPathACO:
    def __init__(self, 
                 n_ants: int = 50,
                 iterations: int = 100,
                 alpha: float = 1.0,
                 beta: float = 2.0,
                 evaporation_rate: float = 0.05,
                 elite_factor: float = 2.0):
        """
        Initialize the ACO path constructor.
        
        Args:
            n_ants: Number of ants in the colony
            iterations: Number of iterations to run
            alpha: Importance of pheromone trails (>0)
            beta: Importance of heuristic information (>0)
            evaporation_rate: Rate of pheromone evaporation (0-1)
            elite_factor: Extra weight for the best ant's trail
        """
        self.n_ants = n_ants
        self.iterations = iterations
        self.alpha = alpha
        self.beta = beta
        self.evaporation_rate = evaporation_rate
        self.elite_factor = elite_factor
        
    def _build_document_graph(self, sections: List[str]) -> Tuple[nx.DiGraph, np.ndarray]:
        """
        Build a graph representation of document sections with similarity-based edges.
        
        Args:
            sections: List of document sections/paragraphs
            
        Returns:
            Tuple of (networkx graph, similarity matrix)
        """
        # Create graph
        G = nx.DiGraph()
        
        # Add nodes (sections)
        for i, section in enumerate(sections):
            G.add_node(i, text=section)
        
        # Calculate TF-IDF vectors for sections
        vectorizer = TfidfVectorizer(stop_words='spanish')
        tfidf_matrix = vectorizer.fit_transform(sections)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Add weighted edges based on similarity
        for i in range(len(sections)):
            for j in range(len(sections)):
                if i != j:  # No self-loops
                    # Edge weight is similarity
                    G.add_edge(i, j, weight=similarity_matrix[i, j])
        
        return G, similarity_matrix
    
    def _initialize_pheromones(self, n_nodes: int) -> np.ndarray:
        """
        Initialize pheromone matrix with small positive values.
        
        Args:
            n_nodes: Number of nodes in the graph
            
        Returns:
            Initial pheromone matrix
        """
        # Start with a small constant value on all edges
        return np.ones((n_nodes, n_nodes)) * 0.1
    
    def _select_next_node(self, 
                         ant_path: List[int],
                         pheromones: np.ndarray,
                         heuristic: np.ndarray,
                         visited_mask: np.ndarray) -> int:
        """
        Select the next node for an ant to visit based on pheromone and heuristic information.
        
        Args:
            ant_path: Current path of the ant
            pheromones: Pheromone matrix
            heuristic: Heuristic information matrix (e.g., similarity)
            visited_mask: Binary mask of visited nodes
            
        Returns:
            Index of the next node to visit
        """
        current_node = ant_path[-1]
        
        # Create mask for unvisited nodes
        unvisited_mask = ~visited_mask
        
        # If all nodes visited, return -1
        if not np.any(unvisited_mask):
            return -1
        
        # Calculate probabilities
        pheromone_factor = pheromones[current_node, :] ** self.alpha
        heuristic_factor = heuristic[current_node, :] ** self.beta
        
        # Ensure we only consider unvisited nodes
        pheromone_factor = pheromone_factor * unvisited_mask
        heuristic_factor = heuristic_factor * unvisited_mask
        
        # Calculate combined factor
        combined_factor = pheromone_factor * heuristic_factor
        
        # If all combined factors are zero, choose randomly from unvisited
        if np.sum(combined_factor) == 0:
            unvisited_indices = np.where(unvisited_mask)[0]
            return np.random.choice(unvisited_indices)
        
        # Calculate probabilities
        probabilities = combined_factor / np.sum(combined_factor)
        
        # Choose next node based on probabilities
        next_node = np.random.choice(len(probabilities), p=probabilities)
        
        return next_node
    
    def _construct_ant_path(self, 
                           start_node: int,
                           n_nodes: int,
                           pheromones: np.ndarray,
                           heuristic: np.ndarray,
                           path_length: int = None) -> List[int]:
        """
        Construct a complete path for an ant.
        
        Args:
            start_node: Starting node index
            n_nodes: Total number of nodes
            pheromones: Pheromone matrix
            heuristic: Heuristic information matrix
            path_length: Maximum path length (if None, visit all nodes)
            
        Returns:
            List of node indices forming the path
        """
        if path_length is None:
            path_length = n_nodes
        
        # Initialize path with start node
        path = [start_node]
        
        # Initialize visited mask
        visited = np.zeros(n_nodes, dtype=bool)
        visited[start_node] = True
        
        # Construct path
        while len(path) < path_length:
            next_node = self._select_next_node(path, pheromones, heuristic, visited)
            
            # If no more nodes to visit, break
            if next_node == -1:
                break
                
            # Add next node to path and mark as visited
            path.append(next_node)
            visited[next_node] = True
        
        return path
    
    def _update_pheromones(self, 
                          pheromones: np.ndarray,
                          all_paths: List[List[int]],
                          path_qualities: List[float]) -> np.ndarray:
        """
        Update pheromone levels based on paths and their qualities.
        
        Args:
            pheromones: Current pheromone matrix
            all_paths: List of paths constructed by ants
            path_qualities: Quality measure for each path
            
        Returns:
            Updated pheromone matrix
        """
        # Evaporation
        pheromones = (1 - self.evaporation_rate) * pheromones
        
        # Find best path
        best_idx = np.argmax(path_qualities)
        best_path = all_paths[best_idx]
        best_quality = path_qualities[best_idx]
        
        # Deposit pheromones for each path
        for path, quality in zip(all_paths, path_qualities):
            for i in range(len(path) - 1):
                from_node = path[i]
                to_node = path[i + 1]
                
                # Add pheromone proportional to path quality
                pheromones[from_node, to_node] += quality
        
        # Elite ant strategy: add extra pheromones to best path
        for i in range(len(best_path) - 1):
            from_node = best_path[i]
            to_node = best_path[i + 1]
            
            # Add extra pheromone for the best path
            pheromones[from_node, to_node] += self.elite_factor * best_quality
        
        return pheromones
    
    def _evaluate_path_quality(self, 
                              path: List[int],
                              similarity_matrix: np.ndarray,
                              node_importance: np.ndarray = None) -> float:
        """
        Evaluate the quality of a path.
        
        Args:
            path: List of node indices
            similarity_matrix: Similarity between nodes
            node_importance: Importance score for each node
            
        Returns:
            Quality score for the path
        """
        if len(path) <= 1:
            return 0.0
        
        # Component 1: Coherence (average similarity between adjacent nodes)
        coherence = 0.0
        for i in range(len(path) - 1):
            coherence += similarity_matrix[path[i], path[i+1]]
        coherence /= (len(path) - 1)
        
        # Component 2: Coverage (diversity of information)
        # Use average pairwise distance between all nodes in the path
        coverage = 0.0
        count = 0
        for i in range(len(path)):
            for j in range(i+1, len(path)):
                coverage += 1.0 - similarity_matrix[path[i], path[j]]
                count += 1
        coverage = coverage / count if count > 0 else 0.0
        
        # Component 3: Importance (if provided)
        importance = 0.0
        if node_importance is not None:
            importance = np.mean([node_importance[node] for node in path])
        else:
            importance = 0.33  # Default when no importance scores
        
        # Combine components
        quality = (0.4 * coherence) + (0.3 * coverage) + (0.3 * importance)
        
        return quality
    
    def find_optimal_path(self, 
                         sections: List[str],
                         start_node: int = 0,
                         path_length: int = None,
                         node_importance: List[float] = None) -> List[str]:
        """
        Find the optimal path through document sections using ACO.
        
        Args:
            sections: List of document sections/paragraphs
            start_node: Index of the starting node
            path_length: Maximum path length (if None, visit all nodes)
            node_importance: Importance score for each node
            
        Returns:
            List of sections in optimal order
        """
        # Build document graph
        G, similarity_matrix = self._build_document_graph(sections)
        n_nodes = len(sections)
        
        # Convert node_importance to numpy array if provided
        node_importance_array = None
        if node_importance is not None:
            node_importance_array = np.array(node_importance)
        
        # Initialize pheromones
        pheromones = self._initialize_pheromones(n_nodes)
        
        # Set default path length if not specified
        if path_length is None:
            path_length = n_nodes
        
        # Best path found so far
        best_path = None
        best_quality = -np.inf
        
        # Main ACO loop
        for iteration in range(self.iterations):
            # Paths constructed by all ants
            all_paths = []
            
            # Let each ant construct a path
            for ant in range(self.n_ants):
                ant_path = self._construct_ant_path(
                    start_node, n_nodes, pheromones, similarity_matrix, path_length
                )
                all_paths.append(ant_path)
            
            # Evaluate path qualities
            path_qualities = [
                self._evaluate_path_quality(path, similarity_matrix, node_importance_array)
                for path in all_paths
            ]
            
            # Update best path if found
            max_quality_idx = np.argmax(path_qualities)
            if path_qualities[max_quality_idx] > best_quality:
                best_path = all_paths[max_quality_idx]
                best_quality = path_qualities[max_quality_idx]
            
            # Update pheromones
            pheromones = self._update_pheromones(pheromones, all_paths, path_qualities)
        
        # Extract ordered sections
        result = [sections[i] for i in best_path]
        
        return result
    
    def analyze_citation_network(self, 
                                citation_graph: nx.DiGraph,
                                start_document: str,
                                max_path_length: int = 5) -> List[Dict]:
        """
        Find the most authoritative path through a citation network using ACO.
        
        Args:
            citation_graph: NetworkX DiGraph representing citation relationships
            start_document: ID of the starting document
            max_path_length: Maximum path length
            
        Returns:
            List of dictionaries with document information
        """
        # Extract nodes and adjacency matrix
        nodes = list(citation_graph.nodes())
        n_nodes = len(nodes)
        
        # Get node indices
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        idx_to_node = {i: node for i, node in enumerate(nodes)}
        
        # Starting node index
        if start_document in node_to_idx:
            start_node_idx = node_to_idx[start_document]
        else:
            # If start document not in graph, use first node
            start_node_idx = 0
        
        # Create heuristic matrix based on citation relationships
        heuristic = np.zeros((n_nodes, n_nodes))
        for i, node_i in enumerate(nodes):
            for j, node_j in enumerate(nodes):
                if citation_graph.has_edge(node_i, node_j):
                    # Edge weight considers both citation and document importance
                    edge_data = citation_graph.get_edge_data(node_i, node_j)
                    weight = edge_data.get('weight', 1.0)
                    heuristic[i, j] = weight
        
        # Calculate node importance using PageRank
        pagerank = nx.pagerank(citation_graph)
        node_importance = np.array([pagerank[node] for node in nodes])
        
        # Initialize pheromones
        pheromones = self._initialize_pheromones(n_nodes)
        
        # Best path found so far
        best_path = None
        best_quality = -np.inf
        
        # Main ACO loop
        for iteration in range(self.iterations):
            # Paths constructed by all ants
            all_paths = []
            
            # Let each ant construct a path
            for ant in range(self.n_ants):
                ant_path = self._construct_ant_path(
                    start_node_idx, n_nodes, pheromones, heuristic, max_path_length
                )
                all_paths.append(ant_path)
            
            # Custom quality function for citation network
            path_qualities = []
            for path in all_paths:
                # Combine PageRank scores and citation weights
                quality = 0.0
                for i in range(len(path) - 1):
                    from_node = idx_to_node[path[i]]
                    to_node = idx_to_node[path[i+1]]
                    
                    if citation_graph.has_edge(from_node, to_node):
                        edge_data = citation_graph.get_edge_data(from_node, to_node)
                        citation_weight = edge_data.get('weight', 1.0)
                        quality += citation_weight * node_importance[path[i+1]]
                
                path_qualities.append(quality / len(path) if len(path) > 0 else 0)
            
            # Update best path if found
            max_quality_idx = np.argmax(path_qualities)
            if path_qualities[max_quality_idx] > best_quality:
                best_path = all_paths[max_quality_idx]
                best_quality = path_qualities[max_quality_idx]
            
            # Update pheromones
            pheromones = self._update_pheromones(pheromones, all_paths, path_qualities)
        
        # Extract document information for the optimal path
        result = []
        for idx in best_path:
            node = idx_to_node[idx]
            doc_info = {
                'id': node,
                'importance': pagerank[node],
                'data': citation_graph.nodes[node]
            }
            result.append(doc_info)
        
        return result
