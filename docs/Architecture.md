# Project Visual Overview

```mermaid
flowchart LR
    A[Next.js Frontend] --> B[Python FastAPI Backend]
    B --> C[Preprocessing & LLM Fine-Tuning]
    C --> D[Neural Networks & ML Models]
    D --> E[Analysis & Error Detection]
    E --> F[Legal Data Integration: BOE and EU]
    F --> G[Enhanced Recommendations Returned to Frontend]
```

## Architecture

- The frontend is built with Next.js to handle user interactions and display results.
- The backend uses Python FastAPI to manage data ingestion, custom LLM fine-tuning, and other ML tasks.
- Preprocessing modules extract textual information, prepare it for neural network analysis, and integrate BOE/EU sources.
- ML components run advanced analysis on incoming documents, highlighting errors and suggesting improvements.
- Results and recommendations are returned to the Next.js application for dynamic user feedback.
