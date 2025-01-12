import streamlit as st
from pipeline import Pipeline
from langchain_community.llms import Ollama

retrieval_vector_store = "../data/vectorstore"
helperPath = "../data/helperData"

llm = Ollama(base_url='http://localhost:11434', model = 'llama3.2')

pipeline = Pipeline(path_vectorstore=retrieval_vector_store, llm=llm)

# Set page configuration
st.set_page_config(page_title="SAMAY", layout="centered")

# App title
st.title("📖 SAMAY - Spiritual Assistance and Meditation Aid for You")

# Input box for user query
query = st.text_input("Enter your query:", placeholder="Ask a question about Sankhya Yoga, Karma Yoga, etc.")

# Button to get the answer
if st.button("Get Answer"):
    if query.strip():
        # Call the GetAnswer function
        answers = pipeline.GetAnswer(query=query)
        st.write(answers)
    else:
        st.error("Please enter a query before submitting.")

# Footer
st.markdown(
    """
    ---
    Developed by Rakshit. Powered by Streamlit and RAG.
    """
)