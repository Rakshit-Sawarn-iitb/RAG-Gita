import numpy as np
from langchain.chains import RetrievalQA
from langchain.llms import CTransformers
from langchain import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()
import google.generativeai as genai

api_key = os.getenv("API_KEY")

# Paths for vector store and metadata
retrieval_vector_store = "../data/vectorstore"
helperPath = "../data/helperData"  # Path to metadata

# Custom Prompt Template
custom_prompt_template = """
You are a wise and enlightened teacher of the Bhagavad Gita. As a spiritual guide, explain in detail the profound teachings on performing one's duties without attachment, drawing from the sacred wisdom of the Bhagavad Gita. Use the following translations of five shlokas to provide a deep, reflective, and insightful answer to the user's question.

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
- Provide explanations that are rich in spiritual and ethical wisdom, connecting the verses to the essence of life, duty (dharma), and the path to self-realization.
- Emphasize the concepts of equanimity, detachment, and the liberation that comes from performing duties selflessly.
- Address the seeker with a compassionate tone, as if guiding them on a path to spiritual enlightenment.
- Do not introduce outside concepts or beliefs, but stay true to the teachings within the Bhagavad Gita.
- If the question is unclear or cannot be answered with the given verses, respond with: "I cannot provide an answer based on the given verses, as the teachings of Bhagavad Gita require a deeper understanding of one's nature and path."
- Always relate the teachings back to the core philosophy of the Bhagavad Gita and its call for inner peace, righteousness, and the fulfillment of one's purpose in life.

Condensed Answer:
"""



# Step 1: Define Custom Prompt
def SetCustomPrompt():
    """
    Creates a custom prompt template for retrieval-based QA.
    """
    return PromptTemplate(
        template=custom_prompt_template,
        input_variables=["context", "metadata_ids", "metadata_speakers", "question", 'shlokas']
    )

# Step 2: Load Language Model
def LoadLLM():
    """
    Loads the Llama-2 model for response generation.
    """
    # return CTransformers(
    #     model="TheBloke/Llama-2-7B-Chat-GGML",
    #     model_type="llama",
    #     max_new_tokens=150,
    #     temperature=0.8,
    #     stop=["Condensed Answer:", "\n\n"]
    # )
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")  
    return model 

# Step 3: Configure the Retrieval-Based QA Chain
def RetrievalQAChain(db):
    """
    Configures the retrieval QA chain with the specified LLM and retriever.
    """
    # return RetrievalQA.from_chain_type(
    #     llm=llm,
    #     chain_type="stuff",
    #     retriever=db.as_retriever(search_kwargs={'k': 5}),
    #     return_source_documents=True
    # )
    return db.as_retriever(search_kwargs={'k': 5})

# Step 4: Create the Bot
def LLamaQABot():
    """
    Creates the QA bot with vector store, metadata, and prompt integration.
    """
    # Load embeddings and vector store
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    db = FAISS.load_local(
        retrieval_vector_store,
        embeddings,
        allow_dangerous_deserialization=True
    )

    # Create retrieval-based QA bot
    qaBot = RetrievalQAChain(db)

    return qaBot

# def clean_output(output):
#     # Remove redundant phrases or excessive repetitions
#     output = " ".join(list(dict.fromkeys(output.split())))
#     return output.strip()

# Step 5: Answer Queries with Context and Metadata
def GetAnswer(query):
    """
    Handles user queries, retrieves context, and integrates metadata into the response.
    """
    llm = LoadLLM()
    qaBot = LLamaQABot()
    # response = qaBot({'query': query})

    # # Extract source documents and metadata
    # documents = response['source_documents']
    retriever = qaBot
    documents = retriever.get_relevant_documents(query)
    if not documents:
        return "No relevant context was found in the Bhagavad Gita to answer this question."

    # Extract metadata
    metadata_ids = [doc.metadata.get('id', 'N/A') for doc in documents]
    metadata_speakers = [doc.metadata.get('speaker', 'Unknown') for doc in documents]
    context = "\n".join([doc.page_content for doc in documents])
    shlokas = [doc.metadata.get('shloka', 'N/A') for doc in documents]

    # Use prompt template to generate response
    custom_prompt = SetCustomPrompt()
    final_prompt = custom_prompt.format(
        context=context,
        metadata_ids=", ".join(metadata_ids),
        metadata_speakers=", ".join(metadata_speakers),
        shlokas=", ".join(shlokas),
        question=query
    )

    # Generate final answer using the LLM
    final_answer = llm.generate_content(final_prompt)
    # final_answer_cleaned = clean_output(final_answer)

    return {
        "answer": final_answer.text,
        "metadata_ids": metadata_ids,
        "metadata_speakers": metadata_speakers,
        "context": context,
        "shlokas":shlokas
    }

# Example Query
if __name__ == "__main__":
    query = "What is the Karma Yoga?"
    response = GetAnswer(query)
    print(f"Retrived Shlokas:\n{response['shlokas']}")
    print(f"Answer:\n{response['answer']}")
    print(f"\nMetadata:\n- Verse IDs: {response['metadata_ids']}\n- Speakers: {response['metadata_speakers']}")
    print(f"\nContext:\n{response['context']}")