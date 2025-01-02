import numpy as np
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
import google.generativeai as genai
from transformers import AutoModelForCausalLM, AutoTokenizer

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

def LoadFineTunedLlamaModel():
    model_name = "RakshitAi/Llama-2-7b-chat-finetune"
    
    # Load the tokenizer
    print("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Load the model
    print("Loading model...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, 
        torch_dtype="auto",  # Automatically select the best precision
        device_map='cpu'    # Distribute the model across available GPUs
    )
    
    print("Model loaded successfully!")
    return model, tokenizer

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
    # print(docs)
    # print(filteredDocs)
    print(scores)
    return filteredDocs


# Step 5: Generate Answer
def GetAnswer(query):
    llm = LoadLLM()
    # llm, tokenizer = LoadFineTunedLlamaModel()
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
    metadata_purport = [doc.metadata.get('purport', 'N/A') for doc in documents]
    flat_metadata_purport = [item for sublist in metadata_purport for item in sublist]

    # Use prompt template to generate response
    custom_prompt = SetCustomPrompt()
    final_prompt = custom_prompt.format(
        context=",".join(flat_metadata_purport),
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
    # inputs = tokenizer(final_prompt, return_tensors="pt")

    # # Generate the response
    # outputs = llm.generate(**inputs, max_length=1024, max_new_tokens=512, temperature=0.7, top_p=0.95)
    # response_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # # Return the response and relevant metadata
    # return {
    #     "answer": response_text,
    #     "metadata_ids": metadata_ids,
    #     "metadata_speakers": metadata_speakers,
    #     "context": context,
    #     "shlokas": shlokas
    # }


# Example Query
if __name__ == "__main__":
    query = "What did sanjay predict about the war?"
    response = GetAnswer(query)
    if isinstance(response, str):
        print(response)
    else:
        print(f"Retrieved Shlokas:\n{response['shlokas']}")
        print(f"Answer:\n{response['answer']}")
        print(f"\nMetadata:\n- Verse IDs: {response['metadata_ids']}\n- Speakers: {response['metadata_speakers']}")
        print(f"\nContext:\n{response['context']}")