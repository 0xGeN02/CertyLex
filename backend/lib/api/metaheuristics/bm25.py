"""
BM25 implementation for ranking documents in legal information retrieval.
This module provides BM25 (Best Matching 25) algorithms for more effective
document searching in BOE legal corpus.
"""

import numpy as np
import math
from typing import List, Dict, Tuple, Any, Union
from collections import Counter
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

class BM25Retrieval:
    def __init__(self, 
                 k1: float = 1.5, 
                 b: float = 0.75,
                 epsilon: float = 0.25):
        """
        Initialize BM25 retrieval model.
        
        Args:
            k1: Term saturation parameter (typical values: 1.2-2.0)
            b: Document length normalization (0.75 is a common value)
            epsilon: Delta for IDF calculation, prevents division by zero
        """
        self.k1 = k1
        self.b = b
        self.epsilon = epsilon
        self.corpus = None
        self.doc_lengths = None
        self.avgdl = None
        self.tf = None
        self.idf = None
        self.doc_freqs = None
        self.n_docs = None
        self.vectorizer = None
        self.vocabulary = None
        
    def _preprocess(self, text: str) -> str:
        """
        Preprocess text for BM25 calculation.
        
        Args:
            text: Raw text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove punctuation, except periods in abbreviations
        text = re.sub(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\w)\.(?=\s)', ' ', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def fit(self, corpus: List[str], use_preprocessor: bool = True):
        """
        Fit BM25 model on a corpus of documents.
        
        Args:
            corpus: List of document texts
            use_preprocessor: Whether to apply preprocessing to documents
        """
        # Preprocess corpus if requested
        if use_preprocessor:
            self.corpus = [self._preprocess(doc) for doc in corpus]
        else:
            self.corpus = corpus
        
        # Number of documents
        self.n_docs = len(self.corpus)
        
        # Create vectorizer for term frequency calculation
        self.vectorizer = CountVectorizer(lowercase=not use_preprocessor)
        X = self.vectorizer.fit_transform(self.corpus)
        
        # Get vocabulary
        self.vocabulary = self.vectorizer.vocabulary_
        
        # Calculate document frequencies (number of documents containing term t)
        self.doc_freqs = np.bincount(X.indices, minlength=len(self.vocabulary))
        
        # Calculate IDF (Inverse Document Frequency)
        # Using the Robertson-Spärck Jones formula with smoothing
        # idf(t) = log((N - n(t) + 0.5) / (n(t) + 0.5) + 1.0)
        self.idf = np.log(
            (self.n_docs - self.doc_freqs + 0.5) / (self.doc_freqs + 0.5) + 1.0
        )
        
        # Calculate document lengths
        self.doc_lengths = X.sum(axis=1).A1
        
        # Calculate average document length
        self.avgdl = np.mean(self.doc_lengths)
        
        # Term frequency matrix
        self.tf = X
        
        return self
    
    def _score_document(self, query_tf: np.ndarray, doc_id: int) -> float:
        """
        Score a single document with respect to the query using BM25 formula.
        
        Args:
            query_tf: Term frequency vector for query
            doc_id: Document ID in the corpus
            
        Returns:
            BM25 score
        """
        # Get document term frequencies
        doc_tf = self.tf[doc_id].toarray().flatten()
        
        # Get length of document
        doc_len = self.doc_lengths[doc_id]
        
        # Calculate BM25 score
        # BM25 formula: 
        # sum(idf(t) * ((k1 + 1) * tf(t)) / (k1 * (1 - b + b * (dl/avgdl)) + tf(t)))
        
        # Document length normalization component
        len_norm = 1.0 - self.b + self.b * (doc_len / self.avgdl)
        
        # For terms that appear in both document and query
        common_terms = np.logical_and(query_tf > 0, doc_tf > 0)
        
        # Calculate score for each common term
        term_scores = np.zeros_like(doc_tf, dtype=np.float64)
        term_scores[common_terms] = self.idf[common_terms] * (
            (self.k1 + 1.0) * doc_tf[common_terms] / 
            (self.k1 * len_norm + doc_tf[common_terms])
        )
        
        # Sum scores for all terms
        return np.sum(term_scores)
    
    def search(self, 
              query: str, 
              top_k: int = 10, 
              use_preprocessor: bool = True) -> List[Dict[str, Any]]:
        """
        Search the corpus using BM25 ranking.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            use_preprocessor: Whether to apply preprocessing to query
            
        Returns:
            List of dictionaries with document ID, text, and score
        """
        if self.corpus is None:
            raise ValueError("Model must be fit before searching")
            
        # Preprocess query if requested
        if use_preprocessor:
            query = self._preprocess(query)
            
        # Convert query to term frequency vector
        query_tf = self.vectorizer.transform([query]).toarray().flatten()
        
        # Score each document
        scores = np.zeros(self.n_docs)
        for doc_id in range(self.n_docs):
            scores[doc_id] = self._score_document(query_tf, doc_id)
            
        # Get top_k documents
        top_indices = np.argsort(-scores)[:top_k]
        
        # Prepare results
        results = []
        for idx in top_indices:
            results.append({
                'id': int(idx),
                'score': float(scores[idx]),
                'text': self.corpus[idx]
            })
            
        return results
    
    def batch_search(self, 
                    queries: List[str], 
                    top_k: int = 10,
                    use_preprocessor: bool = True) -> List[List[Dict[str, Any]]]:
        """
        Perform batch search with multiple queries.
        
        Args:
            queries: List of search queries
            top_k: Number of top results to return per query
            use_preprocessor: Whether to apply preprocessing to queries
            
        Returns:
            List of results for each query
        """
        results = []
        for query in queries:
            results.append(self.search(query, top_k, use_preprocessor))
        return results
    
    def get_term_importance(self, term: str) -> float:
        """
        Get the importance (IDF) of a term in the corpus.
        
        Args:
            term: The term to get importance for
            
        Returns:
            IDF value of the term or 0 if not in vocabulary
        """
        if term not in self.vocabulary:
            return 0.0
        
        term_id = self.vocabulary[term]
        return float(self.idf[term_id])
    
    def calculate_query_importance(self, query: str) -> Dict[str, float]:
        """
        Calculate importance scores for each term in the query.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary mapping terms to their importance scores
        """
        # Preprocess query
        query = self._preprocess(query)
        
        # Get query terms
        terms = query.split()
        
        # Calculate importance
        importance = {}
        for term in terms:
            if term in self.vocabulary:
                term_id = self.vocabulary[term]
                importance[term] = float(self.idf[term_id])
            else:
                importance[term] = 0.0
                
        return importance
