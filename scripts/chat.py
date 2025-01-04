from langchain import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import google.generativeai as genai
import re
from reform import rewrite_query, generate_step_back_query, decompose_query
import pickle
import networkx as nx
import numpy as np

load_dotenv()

api_key = os.getenv("API_KEY")
retrieval_vector_store = "../data/vectorstore4"
helperPath = "../data/helperData4"  # Path to metadata

# Custom Prompt Template
custom_prompt_template = """
You are a wise and enlightened teacher of both the Bhagavad Gita and the Patanjali Yoga Sutras. As a spiritual guide, explain in detail the profound teachings drawn from these sacred texts. Use the following explanations of shlokas and sutras to provide a deep, reflective, and insightful answer to the user's question.

Context:
{context}

Metadata:
- Verse/Sutra IDs: {metadata_ids}
- Speakers: {metadata_speakers}

Texts:
- Shlokas/Sutras: {shlokas}

Question:
{question}

Guidelines:
- Respond as a spiritual teacher imparting timeless wisdom to a seeker.
- Reference the teachings of Bhagwan Krishna, Arjuna, and Patanjali in a manner that feels like a direct and harmonious conversation.
- Frame the response as a journey of understanding, integrating the core principles of both texts. Highlight how the Bhagavad Gita emphasizes duty, devotion, and detachment, while the Patanjali Yoga Sutras emphasize self-discipline, mental control, and spiritual progress through yoga.
- Provide explanations that are rich in spiritual, ethical, and practical wisdom, connecting the teachings to the essence of life.
- Address the seeker with a compassionate tone, as if guiding them on a path to spiritual enlightenment.
- Stay true to the teachings within the Bhagavad Gita and the Patanjali Yoga Sutras. Do not introduce outside concepts or beliefs.
- If the question is unclear or cannot be answered with the given texts, respond with: "I cannot provide an answer based on the given verses or sutras, as the teachings require a deeper understanding of one's nature and path."
- Always relate the teachings back to the core philosophies of the Bhagavad Gita and the Patanjali Yoga Sutras, emphasizing inner peace, righteousness, spiritual discipline, and the fulfillment of one's purpose in life.

Condensed Answer:
"""



# Step 1: Define Custom Prompt
def SetCustomPrompt():
    return PromptTemplate(
        template=custom_prompt_template,
        input_variables=["context", "metadata_ids", "metadata_speakers", "question", 'shlokas']
    )

# Step 2: Load Language Model
def LoadLLM():
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")


# Step 3: Load the Vector Store and Embedding Model
def LoadVectorStore():
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    vector_store = FAISS.load_local(
        retrieval_vector_store,
        embeddings,
        allow_dangerous_deserialization=True
    )
    return vector_store

def load_graph(path="../data/graphs/knowledge_graph.pkl"):
    with open(path, "rb") as f:
        graph = pickle.load(f)
    print("Knowledge graph loaded.")
    return graph

# Step 4: Embed Query and Retrieve Similar Questions
def RetrieveSimilarQuestions(query, vector_store, threshold=0.5, cutoff=2):
    # Step 1: Embed the user query
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    query_embedding = embedding_model.encode([query])

    # Step 2: Perform MMR search
    docs = vector_store.max_marginal_relevance_search(query, k=30, fetch_k=50, lambda_mult=0.9)

    # Step 3: Filter documents by keyword matches
    keywords = set(re.findall(r'\b\w+\b', query.lower()))  # Extract keywords from the query
    keyword_filtered_docs = [
        doc for doc in docs
        if keywords & set(re.findall(r'\b\w+\b', doc.page_content.lower()))
    ]

    # If no keyword matches, fall back to original MMR results
    if not keyword_filtered_docs:
        keyword_filtered_docs = docs

    # Step 4: Further filter documents by similarity score
    final_docs = []
    for doc in keyword_filtered_docs:
        rel = embedding_model.encode([doc.page_content])
        similarity = np.dot(query_embedding, rel.T) / (np.linalg.norm(query_embedding) * np.linalg.norm(rel))
        if similarity >= threshold:
            final_docs.append(doc)

    # Step 5: Use the graph to enhance retrieval
    graph = load_graph()
    related_ids = set()
    for doc in final_docs:
        node_id = doc.metadata['id']
        if node_id in graph:
            # Get related nodes (direct and indirect relationships up to cutoff depth)
            related_ids.update(nx.single_source_shortest_path_length(graph, node_id, cutoff=cutoff).keys())

    # Retrieve graph-enhanced documents
    enhanced_docs = [
        doc for doc in final_docs if doc.metadata['id'] in related_ids
    ]

    return enhanced_docs

# Step 5: Generate Answer
def GetAnswer(query):
    vector_store = LoadVectorStore()
    llm = LoadLLM()
    rewritten_query = rewrite_query(query, llm)
    print(f"Rewritten query: {rewritten_query}")

    # Retrieve similar questions
    documents = RetrieveSimilarQuestions(rewritten_query, vector_store)
    if not documents:
        return "No relevant context was found in the Bhagavad Gita to answer this question."

    # Extract metadata
    metadata_ids = [doc.metadata.get('id', 'N/A') for doc in documents]
    metadata_speakers = [doc.metadata.get('speaker', 'Unknown') for doc in documents]
    metadata_speakers = [", ".join(speaker) if isinstance(speaker, list) else speaker for speaker in metadata_speakers]
    context = "\n".join([doc.page_content for doc in documents])
    shlokas = [doc.metadata.get('shloka', 'N/A') for doc in documents]
    metadata_purport = [doc.metadata.get('purport', 'N/A') for doc in documents]
    flat_metadata_purport = [item for sublist in metadata_purport for item in sublist]

    # Use prompt template to generate response
    custom_prompt = SetCustomPrompt()
    final_prompt = custom_prompt.format(
        context=",".join(flat_metadata_purport),
        metadata_ids=", ".join(metadata_ids),
        metadata_speakers=", ".join(metadata_speakers),
        shlokas=", ".join(shlokas),
        question=rewritten_query
    )

    # Generate final answer using the LLM
    final_answer = llm.generate_content(final_prompt)

    return {
        "answer": final_answer.text,
        "metadata_ids": metadata_ids,
        "metadata_speakers": metadata_speakers,
        "context": context,
        "shlokas": shlokas
    }

# Example Query
if __name__ == "__main__":
    query = "Explain the meaning of Bhagavad Gita Verse 2.47."
    response = GetAnswer(query)
    if isinstance(response, str):
        print(response)
    else:
        print(f"Retrieved Shlokas:\n{response['shlokas']}")
        print(f"Answer:\n{response['answer']}")
        print(f"\nMetadata:\n- Verse IDs: {response['metadata_ids']}\n- Speakers: {response['metadata_speakers']}")
        print(f"\nContext:\n{response['context']}")