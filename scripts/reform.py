from langchain.prompts import PromptTemplate

def rewrite_query(original_query, llm):
    query_rewrite_template = """You are an AI assistant having a deep understanding of the Bhagwad Gita and the Patanjali Yoga Sutras tasked with reformulating user queries to improve retrieval in a RAG system. 
        Given the original query, rewrite it to be more specific, detailed, and likely to retrieve relevant information. But make sure to not add any new information that wasn't present in the original query.

        Original query: {original_query}

        Guidelines:
        - Just provide one rewritten query.
        - No explanations are needed.

        """
    custom_prompt = PromptTemplate(
        template=query_rewrite_template,
        input_variables=["original_query"]
    ) 
    final_prompt = custom_prompt.format(original_query=original_query)
    response = llm(final_prompt)
    return str(response)


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
    response = llm(final_prompt)
    return response


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
    response = llm(final_prompt)
    sub_queries = [q.strip() for q in response.split('\n') if q.strip() and not q.strip().startswith('Sub-queries:')]
    return sub_queries