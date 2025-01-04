# RAG-Gita: An Agentic Retrieval-Augmented Generation System for the Bhagavad Gita

## Overview
RAG-Gita is an advanced Retrieval-Augmented Generation (RAG) system designed to deliver precise, context-rich answers to user queries using the timeless wisdom of the Bhagavad Gita. The system integrates vector search, graph-enhanced relationships, and large language models (LLMs) to provide insightful responses, bridging ancient knowledge with modern AI.

---

## Features

### 1. **Semantic Retrieval Pipeline**
- **FAISS Vector Store**: Implements efficient semantic search with FAISS for dense embeddings of shlokas and their contexts.
- **Keyword Filtering**: Enhances retrieval precision by filtering results based on keyword matches.
- **Graph-Augmented Search**: Utilizes a knowledge graph built with NetworkX to model relationships between shlokas, enabling thematic and sequential retrieval.

### 2. **Query Restructuring**
- Rewrites user queries to align with the text structure of the Bhagavad Gita, reducing hallucinations and improving relevance.
- Uses LLMs to generate step-back and decomposed queries for ambiguous or compound user inputs.

### 3. **Fine-Tuned LLM for Summarization**
- Fine-tuned Llama2 model on a custom dataset of Bhagavad Gita verses, purports, and explanations for domain-specific understanding.
- Summarizes retrieved documents into concise, context-aware answers while maintaining fidelity to the Gita's teachings.

### 4. **Custom Prompting Framework**
- Integrates a spiritual tone in responses with guidelines to reflect the Bhagavad Gita's philosophical themes of duty, devotion, and detachment.
- Supports user interaction as a "seeker," receiving guidance from a wise "teacher."

---

## Architecture

1. **Data Preparation**
   - Verse-wise chunking with metadata (e.g., speakers, translations, purports).
   - Embeddings generated using SentenceTransformers (`all-MiniLM-L6-v2`).

2. **Vector Store**
   - FAISS index for dense retrieval of verses and explanations.
   - Metadata stored for verse identification and contextual relevance.

3. **Knowledge Graph**
   - NetworkX-based graph to model relationships between verses:
     - **Sequential relationships**: Links verses within the same chapter.
     - **Thematic relationships**: Links verses with overlapping purports or translations.

4. **LLM Integration**
   - Retrieval-augmented generation pipeline using Gemini or Llama2 models.
   - Context-aware answer generation through custom prompt templates.

