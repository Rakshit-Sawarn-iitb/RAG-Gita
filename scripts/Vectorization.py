import faiss
import numpy as np
from chunking import chunking_gita
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

chunking_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')
vector_path = '../data/vectorstore'
helperPath = '../data/helperData'
# Step 1: Chunking the Data
def CreateVectorDB():
    chunks = chunking_gita()
    print("Done with chunking")

    # Step 2: Prepare Text for Embedding
    texts_to_embed = [
        chunk['content']['sanskrit'] + " " + " ".join(chunk['content']['translations'].values())
        for chunk in chunks
    ]

    # Step 3: Generate Embeddings
    embeddings = chunking_model.encode(texts_to_embed)
    print("Embeddings generated")

    # Step 4: Create FAISS Index
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

    # Save metadata (IDs, speaker info) alongside the FAISS index
    chunk_metadata = [{'id': chunk['id'], 'speaker': chunk['content']['speaker']} for chunk in chunks]
    np.save(f"{helperPath}/metadata.npy", chunk_metadata)
    faiss.write_index(faiss_index, f"{helperPath}/hybrid_gita.index")

    print("FAISS Created")

    # Step 5: Load into LangChain for Vector Store Management
    # Prepare LangChain documents
    documents = [
        Document(
            page_content=text,
            metadata={'id': chunk['id'], 'speaker': chunk['content']['speaker']}
        )
        for chunk, text in zip(chunks, texts_to_embed)
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