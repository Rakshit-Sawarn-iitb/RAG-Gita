import numpy as np
from langchain.chains import RetrievalQA
from langchain.llms import CTransformers
from langchain import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

# Paths for vector store and metadata
retrieval_vector_store = "../data/vectorstore"
helperPath = "../data/helperData"  # Path to metadata

# Custom Prompt Template
custom_prompt_template = """
You are an expert on the Bhagavad Gita. Here are the translations of five best shlokas summarize them to answer the user's question concisely and to the point.

Context:
{context}

Metadata:
- Verse IDs: {metadata_ids}
- Speakers: {metadata_speakers}

Question:
{question}

Guidelines:
- Frame the response by referencing the speaker where appropriate (e.g., "Arjuna asks" or "Bhagwan Krishna replies").
- Provide a philosophical interpretation directly based on the context.
- Do not add information that is not in the provided context.
- If the answer is not clear from the context, state, "I cannot provide an answer based on the given verses."
- Ensure the response aligns with the teachings of the Bhagavad Gita.

Condensed Answer:
"""

# Step 1: Define Custom Prompt
def SetCustomPrompt():
    """
    Creates a custom prompt template for retrieval-based QA.
    """
    return PromptTemplate(
        template=custom_prompt_template,
        input_variables=["context", "metadata_ids", "metadata_speakers", "question"]
    )

# Step 2: Load Language Model
def LoadLLM():
    """
    Loads the Llama-2 model for response generation.
    """
    return CTransformers(
        model="TheBloke/Llama-2-7B-Chat-GGML",
        model_type="llama",
        max_new_tokens=256,
        temperature=0.9,
        stop=["Condensed Answer:", "\n\n"]
    )

# Step 3: Configure the Retrieval-Based QA Chain
def RetrievalQAChain(llm, db):
    """
    Configures the retrieval QA chain with the specified LLM and retriever.
    """
    return RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=db.as_retriever(search_kwargs={'k': 5}),
        return_source_documents=True
    )

# Step 4: Create the Bot
def LLamaQABot(llm):
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
    qaBot = RetrievalQAChain(llm, db)

    return qaBot

# Step 5: Answer Queries with Context and Metadata
def GetAnswer(query):
    """
    Handles user queries, retrieves context, and integrates metadata into the response.
    """
    llm = LoadLLM()
    qaBot = LLamaQABot(llm)
    response = qaBot({'query': query})

    # Extract source documents and metadata
    documents = response['source_documents']
    if not documents:
        return "No relevant context was found in the Bhagavad Gita to answer this question."

    # Extract metadata
    metadata_ids = [doc.metadata.get('id', 'N/A') for doc in documents]
    metadata_speakers = [doc.metadata.get('speaker', 'Unknown') for doc in documents]
    context = "\n".join([doc.page_content for doc in documents])
    shlokas = [doc.metadata.get('shloka', 'N/A') for doc in documents]

    print(context)
    # Use prompt template to generate response
    custom_prompt = SetCustomPrompt()
    final_prompt = custom_prompt.format(
        context=context,
        metadata_ids=", ".join(metadata_ids),
        metadata_speakers=", ".join(metadata_speakers),
        question=query
    )

    # Generate final answer using the LLM
    final_answer = llm.invoke(final_prompt)

    return {
        "answer": final_answer,
        "metadata_ids": metadata_ids,
        "metadata_speakers": metadata_speakers,
        "context": context,
        "shlokas":shlokas
    }

# Example Query
if __name__ == "__main__":
    query = "What is the importance of performing one's duties without attachment, according to the Bhagavad Gita?"
    response = GetAnswer(query)
    print(f"Retrived Shlokas:\n{response['shlokas']}")
    print(f"Answer:\n{response['answer']}")
    print(f"\nMetadata:\n- Verse IDs: {response['metadata_ids']}\n- Speakers: {response['metadata_speakers']}")
    print(f"\nContext:\n{response['context']}")