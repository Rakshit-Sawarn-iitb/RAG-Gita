import numpy as np
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("API_KEY")
retrieval_vector_store = "../data/vectorstore2"
helperPath = "../data/helperData2"  # Path to metadata

# Custom Prompt Template
custom_prompt_template = """
You are a wise and enlightened teacher of the Bhagavad Gita. As a spiritual guide, explain in detail the profound teachings on performing one's duties without attachment, drawing from the sacred wisdom of the Bhagavad Gita. Use the following translations of five shlokas to provide a deep, reflective, and insightful answer to the user's question. If the question is not related tobhagwad gita then just say that don't ask me irrelevant questions.

Context:
{context}

Metadata:
- Verse IDs: {metadata_ids}
- Speakers: {metadata_speakers}

Shlokas:
- Shlokas: {shlokas}

Question:
{question}

Guidelines:
- Respond as a spiritual teacher imparting timeless wisdom to a seeker.
- Reference the teachings of Bhagwan Krishna and Arjuna in a manner that feels like a direct conversation.
- Frame the response as a journey of understanding, offering deep philosophical insights into performing duties without attachment.
- Provide explanations that are rich in spiritual and ethical wisdom, connecting the verses to the essence of life.
- Emphasize the concepts of equanimity, detachment, and the liberation that comes from performing duties selflessly.
- Address the seeker with a compassionate tone, as if guiding them on a path to spiritual enlightenment.
- Do not introduce outside concepts or beliefs, but stay true to the teachings within the Bhagavad Gita.
- If the question is unclear or cannot be answered with the given verses, respond with: "I cannot provide an answer based on the given verses, as the teachings of Bhagavad Gita require a deeper understanding of one's nature and path."
- Always relate the teachings back to the core philosophy of the Bhagavad Gita and its call for inner peace, righteousness, and the fulfillment of one's purpose in life.

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


# Step 4: Embed Query and Retrieve Similar Questions
def RetrieveSimilarQuestions(query, vector_store, threshold=0.6):
    # Embed the user query
    embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    query_embedding = embedding_model.encode([query])
    

    # Retrieve similar questions
    docs = vector_store.similarity_search_by_vector(query_embedding[0], k=5)
    filteredDocs = []
    scores = []
    for doc in docs:
        rel = embedding_model.encode([doc.page_content])
        similarity = np.dot(query_embedding, rel.T) / (np.linalg.norm(query_embedding) * np.linalg.norm(rel))
        scores.append(similarity[0][0])
        if similarity[0][0] >= threshold:
            filteredDocs.append(doc)
    print(docs)
    print(filteredDocs)
    print(scores)
    return filteredDocs


# Step 5: Generate Answer
def GetAnswer(query):
    llm = LoadLLM()
    vector_store = LoadVectorStore()

    # Retrieve similar questions
    documents = RetrieveSimilarQuestions(query, vector_store)
    if not documents:
        return "No relevant context was found in the Bhagavad Gita to answer this question."

    # Extract metadata
    metadata_translations = [doc.metadata.get('translations', 'N/A') for doc in documents]
    metadata_ids = [doc.metadata.get('id', 'N/A') for doc in documents]
    metadata_speakers = [doc.metadata.get('speaker', 'Unknown') for doc in documents]
    metadata_speakers = [", ".join(speaker) if isinstance(speaker, list) else speaker for speaker in metadata_speakers]
    context = "\n".join([doc.page_content for doc in documents])
    shlokas = [doc.metadata.get('shloka', 'N/A') for doc in documents]
    flat_metadata_translations = [item for sublist in metadata_translations for item in sublist]

    print(flat_metadata_translations)

    # Use prompt template to generate response
    custom_prompt = SetCustomPrompt()
    final_prompt = custom_prompt.format(
        context=",".join(flat_metadata_translations),
        metadata_ids=", ".join(metadata_ids),
        metadata_speakers=", ".join(metadata_speakers),
        shlokas=", ".join(shlokas),
        question=query
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
    query = "What is the weather today?"
    response = GetAnswer(query)
    if isinstance(response, str):
        print(response)
    else:
        print(f"Retrieved Shlokas:\n{response['shlokas']}")
        print(f"Answer:\n{response['answer']}")
        print(f"\nMetadata:\n- Verse IDs: {response['metadata_ids']}\n- Speakers: {response['metadata_speakers']}")
        print(f"\nContext:\n{response['context']}")