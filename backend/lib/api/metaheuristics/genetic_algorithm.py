"""
Genetic Algorithm implementation for extractive text summarization in legal documents.
This module provides a GA-based approach to select the most informative sentences from BOE documents.
"""

import numpy as np
from typing import List, Tuple, Dict, Set
import re
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

class ExtractiveSummarizerGA:
    def __init__(self, 
                 population_size: int = 50,
                 generations: int = 30,
                 summary_size: int = 3,
                 crossover_rate: float = 0.8,
                 mutation_rate: float = 0.2):
        """
        Initialize the GA-based extractive summarizer.
        
        Args:
            population_size: Number of candidate solutions in each generation
            generations: Maximum number of evolutionary iterations
            summary_size: Target number of sentences in summary
            crossover_rate: Probability of performing crossover operation
            mutation_rate: Probability of mutation for each gene
        """
        self.population_size = population_size
        self.generations = generations
        self.summary_size = summary_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using regex for legal text."""
        # Handle specific legal sentence patterns
        text = re.sub(r'(?<=[0-9])\.(?=[0-9])', '<DECIMAL_POINT>', text)  # Protect decimal points
        
        # Split on various sentence terminators, handle legal numbering
        sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÑ])|(?<=\.)\s*\n+\s*(?=[A-ZÁÉÍÓÚÑ0-9])', text)
        
        # Restore decimal points
        sentences = [s.replace('<DECIMAL_POINT>', '.') for s in sentences]
        
        # Clean up sentences
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        return sentences
        
    def _create_sentence_vectors(self, sentences: List[str]) -> np.ndarray:
        """Create TF-IDF vectors for each sentence."""
        vectorizer = TfidfVectorizer(stop_words='spanish')
        tfidf_matrix = vectorizer.fit_transform(sentences)
        return tfidf_matrix
        
    def _initialize_population(self, n_sentences: int) -> List[np.ndarray]:
        """
        Create initial random population of binary vectors.
        Each vector represents which sentences are included in the summary.
        """
        population = []
        for _ in range(self.population_size):
            # Generate random binary vector with exactly summary_size 1's
            individual = np.zeros(n_sentences, dtype=int)
            selected_indices = np.random.choice(
                range(n_sentences), 
                min(self.summary_size, n_sentences), 
                replace=False
            )
            individual[selected_indices] = 1
            population.append(individual)
        return population
        
    def _fitness_function(self, 
                          individual: np.ndarray, 
                          sentence_vectors: np.ndarray, 
                          sentences: List[str]) -> float:
        """
        Calculate fitness of a candidate solution based on:
        1. Coverage: How well the selected sentences cover the main topics
        2. Diversity: Minimizing redundancy between selected sentences
        3. Importance: Prioritizing sentences with higher TF-IDF scores
        4. Position: Giving some weight to sentences appearing earlier
        """
        if np.sum(individual) == 0:
            return 0.0  # No sentences selected
            
        # Get indices of selected sentences
        selected_indices = np.where(individual == 1)[0]
        
        # Calculate coverage score (similarity to the full document)
        document_vector = np.mean(sentence_vectors.toarray(), axis=0).reshape(1, -1)
        summary_vector = np.mean(sentence_vectors[selected_indices].toarray(), axis=0).reshape(1, -1)
        coverage_score = cosine_similarity(document_vector, summary_vector)[0][0]
        
        # Calculate diversity score (penalize redundancy)
        diversity_score = 0.0
        if len(selected_indices) > 1:
            similarities = []
            for i in range(len(selected_indices)):
                for j in range(i+1, len(selected_indices)):
                    sim = cosine_similarity(
                        sentence_vectors[selected_indices[i]].reshape(1, -1),
                        sentence_vectors[selected_indices[j]].reshape(1, -1)
                    )[0][0]
                    similarities.append(sim)
            diversity_score = 1.0 - (sum(similarities) / len(similarities) if similarities else 0)
        
        # Calculate importance score based on TF-IDF values
        importance_score = np.mean([np.sum(sentence_vectors[i].toarray()) for i in selected_indices])
        
        # Position score (favor sentences that appear earlier)
        position_scores = [1.0 - (idx / len(sentences)) for idx in selected_indices]
        position_score = np.mean(position_scores)
        
        # Combine scores with weights
        final_score = (
            0.4 * coverage_score + 
            0.3 * diversity_score + 
            0.2 * importance_score + 
            0.1 * position_score
        )
        
        return final_score
        
    def _tournament_selection(self, 
                              population: List[np.ndarray], 
                              fitness_scores: List[float], 
                              tournament_size: int = 3) -> np.ndarray:
        """Select an individual using tournament selection."""
        # Randomly select tournament_size individuals
        tournament_indices = np.random.choice(len(population), tournament_size, replace=False)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        
        # Return the winner (individual with highest fitness)
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
        
    def _crossover(self, parent1: np.ndarray, parent2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Perform crossover between two parents to create two children."""
        if np.random.random() > self.crossover_rate:
            return parent1.copy(), parent2.copy()
            
        n = len(parent1)
        # One-point crossover
        crossover_point = np.random.randint(1, n)
        
        child1 = np.concatenate([parent1[:crossover_point], parent2[crossover_point:]])
        child2 = np.concatenate([parent2[:crossover_point], parent1[crossover_point:]])
        
        # Ensure each child has exactly summary_size 1's
        for child in [child1, child2]:
            ones_count = np.sum(child)
            if ones_count > self.summary_size:
                # Randomly remove 1's
                ones_indices = np.where(child == 1)[0]
                to_remove = np.random.choice(ones_indices, ones_count - self.summary_size, replace=False)
                child[to_remove] = 0
            elif ones_count < self.summary_size:
                # Randomly add 1's
                zeros_indices = np.where(child == 0)[0]
                to_add = np.random.choice(zeros_indices, self.summary_size - ones_count, replace=False)
                child[to_add] = 1
                
        return child1, child2
        
    def _mutate(self, individual: np.ndarray) -> np.ndarray:
        """Apply mutation to an individual."""
        n = len(individual)
        for i in range(n):
            if np.random.random() < self.mutation_rate:
                # Flip a 0 to 1 and a 1 to 0 to maintain summary_size
                if individual[i] == 1:
                    zeros_indices = np.where(individual == 0)[0]
                    if len(zeros_indices) > 0:
                        j = np.random.choice(zeros_indices)
                        individual[i] = 0
                        individual[j] = 1
                else:
                    ones_indices = np.where(individual == 1)[0]
                    if len(ones_indices) > 0:
                        j = np.random.choice(ones_indices)
                        individual[i] = 1
                        individual[j] = 0
        return individual
        
    def summarize(self, text: str, max_summary_ratio: float = 0.3) -> str:
        """
        Generate an extractive summary of the input text using genetic algorithm.
        
        Args:
            text: The input text to summarize
            max_summary_ratio: Maximum ratio of original text length for summary
            
        Returns:
            Extractive summary as a string
        """
        # Preprocess text
        sentences = self._split_into_sentences(text)
        n_sentences = len(sentences)
        
        if n_sentences <= self.summary_size:
            return text  # Text is already short enough
            
        # Adjust summary size based on text length and max_summary_ratio
        self.summary_size = min(
            self.summary_size,
            max(1, int(n_sentences * max_summary_ratio))
        )
        
        # Create sentence vectors
        sentence_vectors = self._create_sentence_vectors(sentences)
        
        # Initialize population
        population = self._initialize_population(n_sentences)
        
        # Evolution process
        for generation in range(self.generations):
            # Calculate fitness for each individual
            fitness_scores = [
                self._fitness_function(individual, sentence_vectors, sentences)
                for individual in population
            ]
            
            # Keep track of the best individual
            best_idx = np.argmax(fitness_scores)
            best_individual = population[best_idx].copy()
            best_fitness = fitness_scores[best_idx]
            
            # Create new population
            new_population = [best_individual]  # Elitism: keep the best individual
            
            # Fill the rest of the population
            while len(new_population) < self.population_size:
                # Selection
                parent1 = self._tournament_selection(population, fitness_scores)
                parent2 = self._tournament_selection(population, fitness_scores)
                
                # Crossover
                child1, child2 = self._crossover(parent1, parent2)
                
                # Mutation
                child1 = self._mutate(child1)
                child2 = self._mutate(child2)
                
                # Add to new population
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
                    
            # Replace old population
            population = new_population
            
        # Get the best individual from the final population
        final_fitness_scores = [
            self._fitness_function(individual, sentence_vectors, sentences)
            for individual in population
        ]
        best_idx = np.argmax(final_fitness_scores)
        best_individual = population[best_idx]
        
        # Create summary
        selected_indices = np.where(best_individual == 1)[0]
        selected_indices.sort()  # Maintain original order
        summary_sentences = [sentences[i] for i in selected_indices]
        summary = " ".join(summary_sentences)
        
        return summary
