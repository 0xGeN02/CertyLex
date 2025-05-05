"""
Simulated Annealing implementation for parameter optimization tasks in legal document processing.
This module provides a SA-based approach to find optimal parameters for entity detection and model tuning.
"""

import numpy as np
from typing import List, Tuple, Dict, Callable, Any
import time
import random
import math

class SimulatedAnnealingOptimizer:
    def __init__(self, 
                 initial_temp: float = 100.0,
                 cooling_rate: float = 0.95,
                 min_temp: float = 0.1,
                 max_iterations: int = 1000,
                 max_time_seconds: int = 300):
        """
        Initialize the Simulated Annealing optimizer.
        
        Args:
            initial_temp: Starting temperature
            cooling_rate: Rate at which temperature decreases
            min_temp: Termination temperature threshold
            max_iterations: Maximum number of iterations per temperature
            max_time_seconds: Maximum allowed runtime in seconds
        """
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
        self.max_iterations = max_iterations
        self.max_time_seconds = max_time_seconds
        
    def _generate_neighbor(self, 
                           current_solution: Dict[str, Any], 
                           param_ranges: Dict[str, Tuple],
                           temp_ratio: float) -> Dict[str, Any]:
        """
        Generate a neighboring solution by perturbing the current solution.
        The perturbation magnitude decreases as temperature decreases.
        
        Args:
            current_solution: Current parameter values
            param_ranges: Valid ranges for each parameter (min, max)
            temp_ratio: Current temperature ratio (0-1)
            
        Returns:
            A new neighboring solution
        """
        neighbor = current_solution.copy()
        
        # Select random parameter to modify
        param = random.choice(list(current_solution.keys()))
        
        # Get parameter range
        param_min, param_max = param_ranges[param]
        
        # Calculate perturbation magnitude based on temperature
        # Higher temperatures allow larger jumps
        max_perturbation = (param_max - param_min) * temp_ratio
        
        # Generate perturbation
        if isinstance(current_solution[param], int):
            # For integer parameters
            perturbation = random.randint(
                -int(max_perturbation), 
                int(max_perturbation)
            )
            new_value = current_solution[param] + perturbation
            # Ensure new value is within bounds
            new_value = max(param_min, min(param_max, new_value))
            neighbor[param] = int(new_value)
        elif isinstance(current_solution[param], float):
            # For float parameters
            perturbation = random.uniform(-max_perturbation, max_perturbation)
            new_value = current_solution[param] + perturbation
            # Ensure new value is within bounds
            new_value = max(param_min, min(param_max, new_value))
            neighbor[param] = float(new_value)
        elif isinstance(current_solution[param], bool):
            # For boolean parameters, flip with probability based on temperature
            if random.random() < temp_ratio:
                neighbor[param] = not current_solution[param]
        elif isinstance(current_solution[param], str):
            # For categorical parameters, select a different value
            categories = param_ranges[param]
            if len(categories) > 1:  # Only if there are multiple options
                current_idx = categories.index(current_solution[param])
                # Higher probability to select nearby categories when temp is low
                if random.random() < temp_ratio:
                    # Random choice when temp is high
                    new_idx = random.randint(0, len(categories) - 1)
                else:
                    # Limited choice when temp is low
                    max_distance = max(1, int(len(categories) * temp_ratio))
                    distance = random.randint(1, max_distance)
                    direction = random.choice([-1, 1])
                    new_idx = (current_idx + direction * distance) % len(categories)
                neighbor[param] = categories[new_idx]
        
        return neighbor
    
    def optimize(self, 
                initial_solution: Dict[str, Any],
                objective_function: Callable[[Dict[str, Any]], float],
                param_ranges: Dict[str, Tuple],
                maximize: bool = True,
                verbose: bool = False) -> Tuple[Dict[str, Any], float, List[float]]:
        """
        Execute the Simulated Annealing optimization process.
        
        Args:
            initial_solution: Starting parameter values
            objective_function: Function to evaluate solution quality
            param_ranges: Valid ranges for each parameter (min, max)
            maximize: If True, maximize objective function; otherwise minimize
            verbose: Whether to print progress information
            
        Returns:
            Tuple of (best solution, best energy, energy history)
        """
        # Setup
        sign = 1 if maximize else -1  # For maximization or minimization
        start_time = time.time()
        
        current_solution = initial_solution.copy()
        current_energy = sign * objective_function(current_solution)
        
        best_solution = current_solution.copy()
        best_energy = current_energy
        
        temp = self.initial_temp
        energy_history = [current_energy]
        
        iteration = 0
        
        # Main SA optimization loop
        while temp > self.min_temp and time.time() - start_time < self.max_time_seconds:
            for i in range(self.max_iterations):
                iteration += 1
                
                # Check time limit
                if time.time() - start_time >= self.max_time_seconds:
                    break
                
                # Calculate temperature ratio (1.0 at start, approaching 0.0 at end)
                temp_ratio = (temp - self.min_temp) / (self.initial_temp - self.min_temp)
                
                # Generate neighbor
                neighbor = self._generate_neighbor(current_solution, param_ranges, temp_ratio)
                
                # Calculate new energy
                neighbor_energy = sign * objective_function(neighbor)
                
                # Decide whether to accept the new solution
                energy_delta = neighbor_energy - current_energy
                
                # Accept if better
                if energy_delta >= 0:
                    current_solution = neighbor
                    current_energy = neighbor_energy
                    
                    # Update best if this is better
                    if current_energy > best_energy:
                        best_solution = current_solution.copy()
                        best_energy = current_energy
                        if verbose:
                            print(f"New best solution found: Energy = {sign * best_energy}")
                            print(f"Parameters: {best_solution}")
                # Accept with probability based on temperature and energy delta
                elif random.random() < math.exp(energy_delta / temp):
                    current_solution = neighbor
                    current_energy = neighbor_energy
                
                energy_history.append(current_energy)
                
                # Early stopping if we've converged
                if len(energy_history) > 1000 and np.std(energy_history[-1000:]) < 1e-6:
                    if verbose:
                        print("Early stopping due to convergence")
                    break
            
            # Cool down
            temp *= self.cooling_rate
            
            if verbose:
                elapsed = time.time() - start_time
                print(f"Temperature: {temp:.2f}, Iteration: {iteration}, " 
                      f"Best Energy: {sign * best_energy:.4f}, Time: {elapsed:.1f}s")
        
        if verbose:
            print(f"Optimization completed in {time.time() - start_time:.2f} seconds")
            print(f"Final solution: {best_solution}")
            print(f"Final energy: {sign * best_energy}")
        
        # Return the best solution, its energy, and the energy history
        return best_solution, sign * best_energy, [sign * e for e in energy_history]
    
    def optimize_ner_thresholds(self,
                               validation_texts: List[str],
                               validation_entities: List[Dict],
                               ner_function: Callable,
                               initial_thresholds: Dict[str, float] = None) -> Dict[str, float]:
        """
        Optimize NER thresholds using Simulated Annealing.
        
        Args:
            validation_texts: List of texts with known entities
            validation_entities: List of dicts with ground truth entities
            ner_function: Function that takes text and thresholds and returns entities
            initial_thresholds: Starting threshold values
            
        Returns:
            Optimized threshold values
        """
        if initial_thresholds is None:
            initial_thresholds = {
                'person_threshold': 0.5,
                'organization_threshold': 0.5,
                'location_threshold': 0.5,
                'date_threshold': 0.5,
                'misc_threshold': 0.5
            }
        
        # Define parameter ranges
        param_ranges = {
            'person_threshold': (0.1, 0.9),
            'organization_threshold': (0.1, 0.9),
            'location_threshold': (0.1, 0.9),
            'date_threshold': (0.1, 0.9),
            'misc_threshold': (0.1, 0.9)
        }
        
        # Define objective function (F1 score)
        def objective_function(thresholds):
            total_precision = 0
            total_recall = 0
            total_f1 = 0
            
            for text, true_entities in zip(validation_texts, validation_entities):
                # Get predicted entities using current thresholds
                predicted_entities = ner_function(text, thresholds)
                
                # Calculate precision, recall, F1
                true_set = set([(e['type'], e['text']) for e in true_entities])
                pred_set = set([(e['type'], e['text']) for e in predicted_entities])
                
                if not pred_set:
                    precision = 0
                else:
                    precision = len(true_set.intersection(pred_set)) / len(pred_set)
                
                if not true_set:
                    recall = 1
                else:
                    recall = len(true_set.intersection(pred_set)) / len(true_set)
                
                if precision + recall == 0:
                    f1 = 0
                else:
                    f1 = 2 * precision * recall / (precision + recall)
                
                total_precision += precision
                total_recall += recall
                total_f1 += f1
            
            # Average scores across all texts
            avg_f1 = total_f1 / len(validation_texts)
            return avg_f1
        
        # Run optimization
        best_thresholds, best_f1, _ = self.optimize(
            initial_solution=initial_thresholds,
            objective_function=objective_function,
            param_ranges=param_ranges,
            maximize=True,
            verbose=True
        )
        
        return best_thresholds
