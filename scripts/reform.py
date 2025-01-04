from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Function for rewriting a query to improve retrieval
load_dotenv()

api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
def rewrite_query(original_query, llm):
    query_rewrite_template = """You are an AI assistant having a deep understanding of the Bhagwad Gita and the Patanjali Yoga Sutras tasked with reformulating user queries to improve retrieval in a RAG system. 
        Given the original query, rewrite it to be more specific, detailed, and likely to retrieve relevant information. But make sure to not add any new information that wasn't present in the original query.

        Original query: {original_query}

        Rewritten query:"""
    custom_prompt = PromptTemplate(
        template=query_rewrite_template,
        input_variables=["original_query"]
    ) 
    final_prompt = custom_prompt.format(original_query=original_query)
    response = llm.generate_content(final_prompt)
    return response.text


# Function for generating a step-back query to retrieve broader context
def generate_step_back_query(original_query, llm):
    step_back_template = """You are an AI assistant having a deep understanding of the Bhagwad Gita and the Patanjali Yoga Sutras tasked with generating broader, more general queries to improve context retrieval in a RAG system.
        Given the original query, generate a step-back query that is more general and can help retrieve relevant background information.

        Original query: {original_query}

        Step-back query:"""
    custom_prompt = PromptTemplate(
        template=step_back_template,
        input_variables=["original_query"]
    ) 
    final_prompt = custom_prompt.format(original_query=original_query)
    response = llm.generate_content(final_prompt)
    return response.text


# Function for decomposing a query into simpler sub-queries
def decompose_query(original_query, llm):
    subquery_decomposition_template = """You are an AI assistant having a deep understanding of the Bhagwad Gita and the Patanjali Yoga Sutras tasked with breaking down complex queries into simpler sub-queries for a RAG system.
        Given the original query, decompose it into 2-4 simpler sub-queries that, when answered together, would provide a comprehensive response to the original query.

        Original query: {original_query}

        example: What are the impacts of climate change on the environment?

        Sub-queries:
        1. What are the impacts of climate change on biodiversity?
        2. How does climate change affect the oceans?
        3. What are the effects of climate change on agriculture?
        4. What are the impacts of climate change on human health?"""
    custom_prompt = PromptTemplate(
        template=subquery_decomposition_template,
        input_variables=["original_query"]
    ) 
    final_prompt = custom_prompt.format(original_query=original_query)
    response = llm.generate_content(final_prompt).text
    sub_queries = [q.strip() for q in response.split('\n') if q.strip() and not q.strip().startswith('Sub-queries:')]
    return sub_queries


# Main class for the RAG method
class RAGQueryProcessor:
    def __init__(self):
        # Initialize LLM models
        self.re_write_llm = genai.GenerativeModel("gemini-1.5-flash")
        self.step_back_llm = genai.GenerativeModel("gemini-1.5-flash")
        self.sub_query_llm = genai.GenerativeModel("gemini-1.5-flash")

    def run(self, original_query):
        """
        Run the full RAG query processing pipeline.

        Args:
        original_query (str): The original query to be processed
        """
        # Rewrite the query
        rewritten_query = rewrite_query(original_query, self.re_write_llm)
        print("Original query:", original_query)
        print("\nRewritten query:", rewritten_query)

        # Generate step-back query
        step_back_query = generate_step_back_query(original_query, self.step_back_llm)
        print("\nStep-back query:", step_back_query)

        # Decompose the query into sub-queries
        sub_queries = decompose_query(original_query, self.sub_query_llm)
        print("\nSub-queries:")
        for sub_query in sub_queries:
            print(sub_query)



# Main execution
if __name__ == "__main__":
    processor = RAGQueryProcessor()
    query = "What is samadhi?"
    processor.run(query)