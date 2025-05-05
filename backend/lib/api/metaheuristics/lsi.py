"""
Latent Semantic Indexing (LSI) implementation for legal document analysis.
This module provides LSI algorithms for dimensionality reduction and topic modeling
in legal text corpora, particularly for the BOE legal documents.
"""

import numpy as np
from typing import List, Dict, Tuple, Any, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import Normalizer
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

class LSIModel:
    def __init__(self, 
                 n_components: int = 100,
                 random_state: int = 42,
                 use_idf: bool = True,
                 stop_words: Union[str, List[str]] = 'spanish'):
        """
        Initialize LSI model.
        
        Args:
            n_components: Number of topics/components to extract
            random_state: Random seed for reproducibility
            use_idf: Whether to use inverse document frequency weighting
            stop_words: Stop words to exclude ('spanish' or custom list)
        """
        self.n_components = n_components
        self.random_state = random_state
        self.use_idf = use_idf
        self.stop_words = stop_words
        self.vectorizer = None
        self.svd = None
        self.lsi = None
        self.corpus = None
        self.pipeline = None
        self.feature_names = None
        
    def fit(self, corpus: List[str], min_df: int = 2, max_df: float = 0.95):
        """
        Fit LSI model on a corpus of documents.
        
        Args:
            corpus: List of document texts
            min_df: Minimum document frequency for terms
            max_df: Maximum document frequency for terms
        """
        self.corpus = corpus
        
        # Create TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            min_df=min_df,
            max_df=max_df,
            stop_words=self.stop_words,
            use_idf=self.use_idf
        )
        
        # Create SVD decomposition
        self.svd = TruncatedSVD(
            n_components=min(self.n_components, len(corpus) - 1),
            random_state=self.random_state
        )
        
        # Create and fit pipeline
        self.pipeline = Pipeline([
            ('tfidf', self.vectorizer),
            ('svd', self.svd),
            ('normalizer', Normalizer(copy=False))
        ])
        
        # Fit pipeline on corpus
        self.lsi = self.pipeline.fit_transform(corpus)
        
        # Get feature names for later analysis
        self.feature_names = self.vectorizer.get_feature_names_out()
        
        return self
    
    def transform(self, documents: List[str]) -> np.ndarray:
        """
        Transform new documents into the LSI space.
        
        Args:
            documents: List of document texts
            
        Returns:
            Documents in LSI space
        """
        return self.pipeline.transform(documents)
    
    def get_topics(self, n_top_terms: int = 10) -> List[List[Tuple[str, float]]]:
        """
        Get the top terms for each topic.
        
        Args:
            n_top_terms: Number of top terms to include per topic
            
        Returns:
            List of (term, weight) tuples for each topic
        """
        if self.svd is None:
            raise ValueError("Model must be fit before getting topics")
            
        # Get term-topic matrix
        term_topic_matrix = self.svd.components_
        
        topics = []
        for topic_idx, topic in enumerate(term_topic_matrix):
            # Get indices of top terms for this topic
            top_term_indices = np.argsort(-np.abs(topic))[:n_top_terms]
            
            # Get terms and their weights
            topic_terms = [
                (self.feature_names[i], float(topic[i]))
                for i in top_term_indices
            ]
            
            topics.append(topic_terms)
            
        return topics
    
    def search(self, 
              query: str, 
              top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Search the corpus using LSI semantic similarity.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries with document ID, text, and similarity score
        """
        if self.lsi is None:
            raise ValueError("Model must be fit before searching")
            
        # Transform query to LSI space
        query_lsi = self.pipeline.transform([query])
        
        # Calculate similarity with each document
        similarities = cosine_similarity(query_lsi, self.lsi)[0]
        
        # Get top_k documents
        top_indices = np.argsort(-similarities)[:top_k]
        
        # Prepare results
        results = []
        for idx in top_indices:
            results.append({
                'id': int(idx),
                'score': float(similarities[idx]),
                'text': self.corpus[idx]
            })
            
        return results
    
    def find_similar_documents(self, 
                             doc_id: int, 
                             top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Find documents similar to a given document.
        
        Args:
            doc_id: ID of the document to find similar documents to
            top_k: Number of similar documents to return
            
        Returns:
            List of dictionaries with document ID, text, and similarity score
        """
        if self.lsi is None or doc_id >= len(self.lsi):
            raise ValueError("Invalid document ID or model not fit")
            
        # Get document vector in LSI space
        doc_lsi = self.lsi[doc_id].reshape(1, -1)
        
        # Calculate similarity with all documents
        similarities = cosine_similarity(doc_lsi, self.lsi)[0]
        
        # Get top_k+1 documents (including the query document)
        top_indices = np.argsort(-similarities)[:top_k+1]
        
        # Remove the query document itself
        top_indices = top_indices[top_indices != doc_id][:top_k]
        
        # Prepare results
        results = []
        for idx in top_indices:
            results.append({
                'id': int(idx),
                'score': float(similarities[idx]),
                'text': self.corpus[idx]
            })
            
        return results
    
    def get_document_topics(self, 
                         doc_id: int, 
                         threshold: float = 0.1) -> List[Tuple[int, float]]:
        """
        Get the topics most associated with a document.
        
        Args:
            doc_id: ID of the document
            threshold: Minimum weight to include a topic
            
        Returns:
            List of (topic_id, weight) tuples
        """
        if self.lsi is None or doc_id >= len(self.lsi):
            raise ValueError("Invalid document ID or model not fit")
            
        # Get document vector in LSI space
        doc_vector = self.lsi[doc_id]
        
        # Get topics above threshold
        topic_weights = [(i, abs(weight)) for i, weight in enumerate(doc_vector)]
        significant_topics = [t for t in topic_weights if t[1] >= threshold]
        
        # Sort by weight
        significant_topics.sort(key=lambda x: x[1], reverse=True)
        
        return significant_topics
    
    def get_explained_variance(self) -> np.ndarray:
        """
        Get the explained variance for each component.
        
        Returns:
            Array of explained variance ratios
        """
        if self.svd is None:
            raise ValueError("Model must be fit before getting explained variance")
            
        return self.svd.explained_variance_ratio_
    
    def visualize_topics(self, 
                        output_dir: str = None,
                        n_top_terms: int = 15,
                        figsize: Tuple[int, int] = (15, 10)) -> None:
        """
        Visualize topics as word clouds.
        
        Args:
            output_dir: Directory to save visualizations (if None, just display)
            n_top_terms: Number of top terms to include per topic
            figsize: Figure size for plots
        """
        if self.svd is None:
            raise ValueError("Model must be fit before visualizing topics")
            
        # Get topics
        topics = self.get_topics(n_top_terms=50)  # Get more terms for better clouds
        
        # Create output directory if needed
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Number of topics to visualize (max 9 for a 3x3 grid)
        n_topics = min(9, len(topics))
        
        # Create figure
        fig, axs = plt.subplots(3, 3, figsize=figsize)
        axs = axs.flatten()
        
        for topic_idx, topic_terms in enumerate(topics[:n_topics]):
            # Create word cloud data
            word_cloud_data = {term: abs(weight) for term, weight in topic_terms}
            
            # Generate word cloud
            wordcloud = WordCloud(
                background_color='white',
                width=400,
                height=400,
                colormap='viridis',
                max_words=n_top_terms
            ).generate_from_frequencies(word_cloud_data)
            
            # Plot word cloud
            axs[topic_idx].imshow(wordcloud, interpolation='bilinear')
            axs[topic_idx].set_title(f'Topic {topic_idx+1}')
            axs[topic_idx].axis('off')
            
        # Hide empty subplots
        for idx in range(n_topics, len(axs)):
            axs[idx].axis('off')
            
        plt.tight_layout()
        
        # Save or display
        if output_dir:
            plt.savefig(os.path.join(output_dir, 'lsi_topics.png'), dpi=300)
        else:
            plt.show()
            
        plt.close()
    
    def find_topics_for_query(self, 
                            query: str, 
                            threshold: float = 0.1) -> List[Tuple[int, float]]:
        """
        Find topics most related to a query.
        
        Args:
            query: Query text
            threshold: Minimum weight to include a topic
            
        Returns:
            List of (topic_id, weight) tuples
        """
        # Transform query to LSI space
        query_lsi = self.pipeline.transform([query])[0]
        
        # Get topics above threshold
        topic_weights = [(i, abs(weight)) for i, weight in enumerate(query_lsi)]
        significant_topics = [t for t in topic_weights if t[1] >= threshold]
        
        # Sort by weight
        significant_topics.sort(key=lambda x: x[1], reverse=True)
        
        return significant_topics
