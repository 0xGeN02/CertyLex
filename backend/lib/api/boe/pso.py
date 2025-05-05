import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class PSODocumentRetrieval:
    def __init__(self, documents, n_particles=20, iterations=50):
        self.documents = documents
        self.n_particles = n_particles
        self.iterations = iterations
        self.dimensions = 10  # Feature weights dimensions
        
    def initialize_swarm(self):
        # Initialize particles with random positions and velocities
        positions = np.random.random((self.n_particles, self.dimensions))
        velocities = np.random.random((self.n_particles, self.dimensions)) * 0.1
        return positions, velocities
        
    def fitness_function(self, weights, query_vector, relevant_docs):
        # Apply weights to document vectors
        weighted_docs = [doc_vector * weights for doc_vector in self.document_vectors]
        
        # Calculate similarity scores
        scores = [cosine_similarity(query_vector.reshape(1, -1), 
                                  doc.reshape(1, -1))[0][0] for doc in weighted_docs]
                                  
        # Calculate precision/recall against known relevant documents
        # Return fitness score (higher is better)
        return precision_recall_score(scores, relevant_docs)
        
    def update_position(self, positions, velocities):
        # PSO position update rules
        return positions + velocities
        
    def update_velocity(self, positions, velocities, p_best, g_best):
        # PSO velocity update with inertia, cognitive and social components
        w = 0.7  # Inertia weight
        c1 = 1.5  # Cognitive parameter
        c2 = 1.5  # Social parameter
        
        r1, r2 = np.random.random(2)
        
        new_velocities = (w * velocities + 
                          c1 * r1 * (p_best - positions) + 
                          c2 * r2 * (g_best - positions))
        return new_velocities
        
    def optimize(self, query, relevant_docs):
        # Main PSO optimization loop
        positions, velocities = self.initialize_swarm()
        p_best = positions.copy()
        p_best_fitness = np.zeros(self.n_particles)
        g_best = None
        g_best_fitness = -np.inf
        
        for iteration in range(self.iterations):
            # Evaluate fitness for each particle
            for i in range(self.n_particles):
                fitness = self.fitness_function(positions[i], query, relevant_docs)
                
                # Update personal best
                if fitness > p_best_fitness[i]:
                    p_best_fitness[i] = fitness
                    p_best[i] = positions[i].copy()
                
                # Update global best
                if fitness > g_best_fitness:
                    g_best_fitness = fitness
                    g_best = positions[i].copy()
            
            # Update velocities and positions
            velocities = self.update_velocity(positions, velocities, p_best, g_best)
            positions = self.update_position(positions, velocities)
            
        return g_best, g_best_fitness