# CertyLex Agent

This project is designed to implement neural networks to analyze legal documents by incorporating official sources such as the Spanish BOE and European legal frameworks. Once the user uploads a legal document, an advanced preprocessing pipeline along with machine learning agents and natural language processing techniques detects errors, suggests improvements, and provides contextual recommendations in line with current legal standards.

## Contents

- [CertyLex Agent](#certylex-agent)
  - [Contents](#contents)
  - [Overview](#overview)
  - [Features](#features)
  - [Preprocessing \& Analysis Workflow](#preprocessing--analysis-workflow)
  - [Integration with Official Sources](#integration-with-official-sources)
  - [Usage](#usage)
  - [Contributing](#contributing)
  - [License](#license)
  - [Full-Stack Setup](#full-stack-setup)
  - [Metaheuristic Algorithms](#metaheuristic-algorithms)
    - [Particle Swarm Optimization (PSO)](#particle-swarm-optimization-pso)
      - [Implementation Details](#implementation-details)
      - [Use Cases in CertyLex](#use-cases-in-certylex)
    - [Genetic Algorithms (GA)](#genetic-algorithms-ga)
      - [Implementation Details1](#implementation-details1)
      - [Use Cases in CertyLex1](#use-cases-in-certylex1)
    - [Simulated Annealing (SA)](#simulated-annealing-sa)
      - [Implementation Details2](#implementation-details2)
      - [Use Cases in CertyLex2](#use-cases-in-certylex2)
    - [Ant Colony Optimization (ACO)](#ant-colony-optimization-aco)
      - [Implementation Details3](#implementation-details3)
      - [Use Cases in CertyLex3](#use-cases-in-certylex3)
    - [Additional Retrieval Algorithms](#additional-retrieval-algorithms)
  - [Project Corpus Overview](#project-corpus-overview)
    - [Structure](#structure)
    - [Dataset Usage](#dataset-usage)
    - [Machine Learning Considerations](#machine-learning-considerations)
      - [Model Training Pipeline](#model-training-pipeline)
      - [Emphasis on the Corpus](#emphasis-on-the-corpus)
    - [Notes](#notes)

## Overview

Contract Manager Neural Edition leverages one or more neural networks along with a sophisticated preprocessing pipeline to evaluate, optimize, and ensure the legal compliance of documents. The system enriches its analysis by accessing information from the Spanish BOE and European regulatory bodies, providing users with targeted feedback that aligns their documents with current legislative requirements.

## Features

- **Text Preprocessing:** Cleans, normalizes, and extracts key features from the document.
- **Neural Analysis:** Utilizes deep learning algorithms to evaluate content automatically.
- **Error Detection & Suggestions:** Precisely identifies areas requiring corrections or improvements.
- **Machine Learning Agents:** Integrates intelligent agents to adapt and improve analysis techniques continuously.
- **Natural Language Processing (NLP):** Employs advanced NLP to understand and process legal language.
- **Official Legal Integration:** Retrieves and incorporates updates from the Spanish BOE and European legal sources to contextualize recommendations.
- **Interactive Feedback:** Generates real-time reports with actionable insights and enhancement suggestions.

## Preprocessing & Analysis Workflow

1. **Document Upload:** The user submits a legal document through the provided interface.
2. **Preprocessing:** The document is cleaned, normalized, and key features are extracted.
3. **Neural Analysis:** Neural networks and ML agents process the content to detect errors, extract patterns, and identify improvement opportunities.
4. **Official Data Integration:** Information from the Spanish BOE and European legal sources is fetched to validate and enhance the analysis context.
5. **Results Presentation:** Detailed, interactive reports are generated with specific recommendations and legislative references.

## Integration with Official Sources

- **Spanish BOE:** The system connects to the official BOE database to retrieve the latest legislative updates affecting legal documents.
- **European Legislation:** The analysis process also references European legal frameworks and directives to ensure a comprehensive evaluation.
- **Dynamic Updates:** Frequent updates from official sources ensure that recommendations remain current and legally compliant.

## Usage

- **Upload Document:** Submit your legal document using the designated interface.
- **Review Analysis:** Access the detailed report with recommendations for improvement, including references to relevant legal publications.
- **Implement Suggestions:** Apply the proposed changes to optimize your document in compliance with current Spanish and European regulations.

## Contributing

Contributions are welcome; however, please note that this project is closed source. For inquiries regarding contributions, collaboration details, or access to specific modules, contact the project maintainers.

## License

This project is proprietary and closed source. All rights reserved.

## Full-Stack Setup

This project consists of a **Next.js full-stack** and a **Python FastAPI backend**. Follow the steps at [SETUP.md](./SETUP.md).

## Metaheuristic Algorithms

CertyLex employs sophisticated metaheuristic algorithms to optimize various aspects of legal document processing, information retrieval, and analysis. These algorithms provide adaptive solutions to complex optimization problems encountered in legal text analysis.

### Particle Swarm Optimization (PSO)

PSO is a population-based stochastic optimization technique inspired by the social behavior of birds flocking or fish schooling.

#### Implementation Details

- **Document Vector Weights**: PSO optimizes the importance weights assigned to different features in document vectors
- **Parameter Space**: Each particle represents a unique configuration of retrieval parameters
- **Convergence**: Typically reaches good solutions within 50-100 iterations
- **Hyperparameters**: Inertia weight (0.7), cognitive coefficient (1.5), social coefficient (1.5)

#### Use Cases in CertyLex

- Optimizing query expansion parameters
- Fine-tuning document chunking strategies
- Balancing precision vs. recall in legal document retrieval

### Genetic Algorithms (GA)

GA is an evolutionary algorithm that mimics the process of natural selection, using mechanisms like selection, crossover, and mutation.

#### Implementation Details1

- **Chromosome Representation**: Binary encoding of document segments for extractive summarization
- **Fitness Function**: Measures information coverage and semantic coherence
- **Selection Method**: Tournament selection with elitism
- **Crossover Rate**: 0.8
- **Mutation Rate**: 0.1

#### Use Cases in CertyLex1

- Extractive summarization of BOE documents
- Optimizing feature combinations for NER tasks
- Evolving rule patterns for legal entity extraction

### Simulated Annealing (SA)

SA is a probabilistic technique for approximating the global optimum of a function, inspired by the annealing process in metallurgy.

#### Implementation Details2

- **Temperature Schedule**: Exponential cooling from 100 to 0.1
- **Neighborhood Function**: Randomized perturbation of solution parameters
- **Acceptance Probability**: Boltzmann distribution
- **Iterations**: 1000 per temperature level

#### Use Cases in CertyLex2

- Fine-tuning NER model parameters
- Optimizing threshold values for entity detection
- Scheduling document batch processing

### Ant Colony Optimization (ACO)

ACO is inspired by the foraging behavior of ant colonies, using pheromone trails to identify optimal paths.

#### Implementation Details3

- **Pheromone Representation**: Graph with document segments as nodes
- **Heuristic Information**: TF-IDF scores and semantic similarity
- **Evaporation Rate**: 0.05
- **Colony Size**: 50 ants per iteration

#### Use Cases in CertyLex3

- Building optimal paths through document sections
- Constructing extractive summaries
- Identifying key citation networks in legal documents

### Additional Retrieval Algorithms

CertyLex also implements several specialized algorithms to enhance document retrieval:

1. **BM25 Ranking Algorithm**: Enhances keyword-based search with better relevance ranking than TF-IDF alone
2. **Latent Semantic Indexing (LSI)**: Captures semantic relationships between legal terms
3. **Graph-based PageRank for Legal Citations**: Identifies authoritative legal documents
4. **K-Nearest Neighbors (KNN) Classification**: Automatically categorizes and tags legal documents
5. **HDBSCAN Clustering**: Discovers document clusters without predefined categories
6. **FAISS (Facebook AI Similarity Search)**: Scales vector similarity search for millions of documents

## Project Corpus Overview

This repository contains a large corpus of Spanish Official State Bulletins stored under `data/boe/*`. The corpus spans daily summaries from 2010-01-01 to 2025-03-22, with around 400,000 XML files. Each file represents official legal documents, litigation records, and other notices published in the Boletín Oficial del Estado (BOE).

### Structure

- **data/boe/[year]/[date]/xml/...**  
  // ...existing code or directories...

### Dataset Usage

- This dataset can be used for various text mining and natural language processing tasks, including entity recognition and classification.
- The XML format provides metadata fields, references to PDF versions, and text segments for deeper parsing.

### Machine Learning Considerations

- **Preprocessing**: Tokenize and structure the XML content to extract relevant fields.  
- **Annotation**: Identify named entities such as institutions, legislation titles, or legal references.  
- **Modeling**: Train classification or summary models on curated sections to predict legal categories or case topics.

#### Model Training Pipeline

1. **Data Extraction**: Parse each XML file to extract structured fields (e.g., metadata, text content).
2. **Data Cleaning**: Handle inconsistencies, remove duplicates, and organize data by date and domain.
3. **Feature Engineering**: Tokenize and normalize legal terms, detect named entities, and encode relationships.
4. **Model Selection**: Evaluate candidate architectures (e.g., transformers, RNNs) using subsets of the corpus.
5. **Training & Validation**: Train ML models to classify, summarize, or otherwise analyze legal documents, leveraging the large volume of corpus data.
6. **Deployment**: Integrate the trained model into the application pipeline to provide automated insights.

#### Emphasis on the Corpus

- This massive corpus of ~400,000 XML files offers detailed daily summaries from 2010-01-01 to 2025-03-22.
- Each file includes legal and administrative notices crucial for robust NLP tasks.
- Harnessing extensive historical and future data enhances model accuracy and generalization across various legal domains.

### Notes

- Ensure you have appropriate permissions to handle the data.  
- For large-scale ML training, consider parallel or distributed processing due to the high volume of files.
