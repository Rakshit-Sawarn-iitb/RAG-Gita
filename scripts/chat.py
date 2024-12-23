from langchain.chains import RetrievalQA
from langchain.llms import CTransformers
from langchain import PromptTemplate
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

retrieval_vector_store = "../data/vectorstore"

custom_prompt_template = """
You are an expert on the Bhagavad Gita. Use the following verses and their explanations to answer the user's question concisely and to the point.

Context:
{context}

Question:
{question}

Guidelines:
- Provide a philosophical interpretation directly based on the context.
- Do not add information that is not in the provided context.
- If the answer is not clear from the context, state, "I cannot provide an answer based on the given verses."
- Ensure the response aligns with the teachings of the Bhagavad Gita.

Condensed Answer:
"""
def SetCustomPrompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt


def LoadLLM():
    llm = CTransformers(
        model = "TheBloke/Llama-2-7B-Chat-GGML",
        model_type="llama",
        max_new_tokens = 512,
        temperature = 0.5
    )
    return llm

def RetrievalQAChain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff', retriever=db.as_retriever(search_kwargs={'k': 5}), 
                                           return_source_documents=True, chain_type_kwargs={'prompt': prompt})
    return qa_chain

def LLamaQABot():
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(retrieval_vector_store, embeddings, allow_dangerous_deserialization=True)

    llm = LoadLLM()
    qaPropmpt = SetCustomPrompt()
    qaBot = RetrievalQAChain(llm,qaPropmpt,db)

    return  qaBot

def GetAnswer(query):
    qaBot = LLamaQABot()
    response = qaBot({'query':query})

    return response

response = GetAnswer("What is the importance of performing one's duties without attachment, according to the Bhagavad Gita?")
print(response)