# Leveraging Retrieval-Augmented Generation for the Study and Interpretation of Religious Texts
# SAMAY - Spiritual Assistance and Meditation Aid for You

## Overview
SAMAY is an advanced Retrieval-Augmented Generation (RAG) system designed to deliver precise, context-rich answers to user queries using the timeless wisdom of the Bhagavad Gita and the Patanjali Yoga Sutras. The system integrates vector search, BM25 Scores, fusion retrieval methods, and large language models (LLMs) to provide insightful responses, bridging ancient knowledge with modern AI.

---

## Features

### 1. **Retrieval Pipeline**
- **FAISS Vector Store**: Provides similarity scores for the documents.
- **BM25 Retriever**: Provides BM25 scores for the documents.
- **Fusion Retrieval**: Calculates weighted score and then filter out the relevant documents accordingly.

### 2. **Query Restructuring**
- Rewrites user queries to align with the text structure of the Bhagavad Gita, reducing hallucinations and improving relevance.
- Uses LLMs to generate step-back and decomposed queries for ambiguous or compound user inputs.

### 3. **LLM for Summarization**
- Llama3.2 model summarizes retrieved documents into concise, context-aware answers while maintaining fidelity to the Gita's teachings.

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

3. **LLM Integration**
   - Retrieval-augmented generation pipeline using Llama3.
   - Context-aware answer generation through custom prompt templates.

## For detailed documentation
Visit this Notion page https://abiding-museum-395.notion.site/Leveraging-Retrieval-Augmented-Generation-for-the-Study-and-Interpretation-of-Religious-Texts-179e5c02a97380198b3adcfc256b02bb

## Running Instructions

Clone the repo by `git clone https://github.com/Rakshit-Sawarn-iitb/RAG-Gita.git`

### Make sure you have Ollama installed on your PC
Pull the LLama3.2 model by `ollama pull llama3.2`

1. Create a virtual environment
2. Activate your virtual environment
3. Install requirements using
   `pip install -r requirements.txt`
### You are done with the setup

Now, Go to scripts folder and run this in your terminal `streamlit run interface.py`

### And use SAMAY
