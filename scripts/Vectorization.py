import numpy as np
import faiss
from chunking import chunking
from sentence_transformers import SentenceTransformer
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

#Paths for storing vector and metadata
chunking_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
vector_path = '../data/vectorstore'
helper_path = '../data/helperData'

#Chunking the Data
def CreateVectorDB():
    # Chunking the data
    chunks = chunking()
    print("Done with chunking")

    #Prepare Texts and Metadata for Embedding
    texts_to_embed = []
    metadata_list = []

    for chunk in chunks:
        combined_questions = chunk['questions']
        texts_to_embed.append(combined_questions)
        metadata_list.append({
            'speaker': chunk['speakers'],
            'shloka': chunk['sanskrit'],
            'chapter': chunk['chapter'],
            'verse': chunk['verse'],
            'source':chunk['source'],
            'translations': chunk['translations'],
            'purport': chunk['purports']
        })

    print(f"Total clusters to embed: {len(texts_to_embed)}")

    #Generate Embeddings
    embeddings = chunking_model.encode(texts_to_embed, show_progress_bar=True)
    print("Embeddings generated")

    #Create and Save FAISS Index
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

    #Save metadata and FAISS index
    np.save(f"{helper_path}/metadata.npy", metadata_list)
    faiss.write_index(faiss_index, f"{helper_path}/hybrid_gita_questions.index")
    print("FAISS Index Created")

    #Integrate FAISS into LangChain
    documents = [
        Document(page_content=text, metadata=meta)
        for text, meta in zip(texts_to_embed, metadata_list)
    ]

    hf_embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    vector_store = FAISS.from_documents(documents, hf_embeddings)

    # Save the LangChain vector store
    vector_store.save_local(vector_path)
    print("LangChain Vector Store Created and Saved")

if __name__ == "__main__":
    print("Vector Database creation in progress.")
    CreateVectorDB()