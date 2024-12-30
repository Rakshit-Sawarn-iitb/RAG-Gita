import faiss
import numpy as np
from chunking import chunking_gita
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

chunking_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
vector_path = '../data/vectorstore2'
helperPath = '../data/helperData2'
# Step 1: Chunking the Data
def CreateVectorDB():
    chunks = chunking_gita()
    print("Done with chunking")

    # Step 2: Combine Questions for Each Verse
    texts_to_embed = []
    metadata_list = []

    for chunk in chunks:
        questions = chunk['content']['questions']
        combined_questions = " ".join(questions) if isinstance(questions, list) else questions
        texts_to_embed.append(combined_questions)
        metadata_list.append({
            'id': chunk['id'],
            'speaker': chunk['content']['speakers'],
            'shloka': chunk['content']['sanskrit'],
            'chapter': chunk['id'].split('-')[1],
            'verse': chunk['id'].split('-')[-1],
            'translations': chunk['content']['translations']
        })

    print(f"Total verses to embed: {len(texts_to_embed)}")

    # Step 3: Generate Embeddings
    embeddings = chunking_model.encode(texts_to_embed)
    print("Embeddings generated")

    # Step 4: Create FAISS Index
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

    # Save metadata (IDs, speaker info) alongside the FAISS index
    np.save(f"{helperPath}/metadata.npy", metadata_list)
    faiss.write_index(faiss_index, f"{helperPath}/hybrid_gita_questions.index")

    print("FAISS Created")

    # Step 5: Load into LangChain for Vector Store Management
    # Prepare LangChain documents
    documents = [
        Document(
            page_content=combined_questions,
            metadata=metadata
        )
        for combined_questions, metadata in zip(texts_to_embed, metadata_list)
    ]

    # Use LangChain's FAISS wrapper
    hf_embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vector_store = FAISS.from_documents(documents, hf_embeddings)

    print("Vector Store Created")

    # Save LangChain vector store
    vector_store.save_local(vector_path)

if __name__ == "__main__":
    print("Vector Database creation in progress.")
    CreateVectorDB()
