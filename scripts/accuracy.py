from retriever import Retriever
import pandas as pd
from tqdm import tqdm 
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate

data = pd.read_csv("../data/processed/final.csv")
retrieval_vector_store = "../data/vectorstore"
helperPath = "../data/helperData"

llm = Ollama(base_url='http://localhost:11434', model = 'llama3.2')

class Accuracy():
    def __init__(self, vectorstorepath, data, llm=None):
        self.vectorstorepath = vectorstorepath
        self.data = data
        self.llm = llm

    def LoadVectorStore(self):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        vector_store = FAISS.load_local(
            self.vectorstorepath,
            embeddings,
            allow_dangerous_deserialization=True
        )
        return vector_store

    def GetAccuracyRuleBased(self):
        accuracy = 0
        vectorstore = self.LoadVectorStore()

        with tqdm(range(len(data)), desc="Calculating Accuracy", unit="query") as pbar:
            for i in pbar:
                query = data['question'].iloc[i]
                similar_questions = Retriever(query, vectorstore=vectorstore).samay()
                similar_questions_split = [
                    q+'?' for doc in similar_questions
                    for q in doc.page_content.split('?') if q.strip()
                ]
                if data['question'].iloc[i] in similar_questions_split:
                    accuracy += 1

                current_accuracy = accuracy / (i + 1)
                pbar.set_description(f"Calculating Accuracy (Current: {current_accuracy:.2%})")

        # Return final accuracy
        return accuracy / len(data)
    
    def GetAccuracyLLM(self):
        accuracy = 0
        vectorstore = self.LoadVectorStore()
        prompt_template = PromptTemplate(
            input_variables=["query", "doc"],
            template="""Determine if the following document directly answers the query. Respond with "Yes" if it does, otherwise "No".
            Query: {query}
            Document: {doc}

            Guidelines:
            - No explanation is required.
            - No other text is required.
            - Just provide yes or no
            """
        )

        with tqdm(range(len(data)), desc="Calculating Accuracy", unit="query") as pbar:
            for i in pbar:
                query = data['question'].iloc[i]
                similar_docs = Retriever(query, vectorstore=vectorstore).samay()
                
                # LLM-based comparison
                match_found = False
                for doc in similar_docs:
                    prompt = prompt_template.format(query=query, doc=doc.page_content)
                    response = self.llm(prompt)
                    if response.strip().lower().rstrip('.') == "yes":
                        match_found = True
                        break

                if match_found:
                    accuracy += 1
                
                current_accuracy = accuracy / (i + 1)
                pbar.set_description(f"Calculating Accuracy (Current: {current_accuracy:.2%})")

        return accuracy / len(data)

if __name__ == "__main__":
    accuracy = Accuracy(data=data, vectorstorepath=retrieval_vector_store, llm=llm)
    final_accuracy_rule_based = accuracy.GetAccuracyRuleBased()
    final_accuracy_llm_based = accuracy.GetAccuracyLLM()
    print(f"Final Accuracy Rule Based: {final_accuracy_rule_based:.2%}")
    print(f"Final Accuracy LLM Based: {final_accuracy_llm_based:.2%}")
