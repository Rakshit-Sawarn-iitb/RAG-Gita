from langchain.prompts import PromptTemplate
from rank_bm25 import BM25Okapi
from typing import List
from langchain.docstore.document import Document
import numpy as np

class Retriever():
    def __init__(self, query, vectorstore, k=15, top_n=5, alpha = 0.5, llm=None):
        self.llm = llm
        self.query = query
        self.vectorstore = vectorstore
        self.k = k
        self.n = top_n
        self.alpha = alpha

    def create_bm25_index(self, documents: List[Document]) -> BM25Okapi:
        tokenized_docs = [doc.page_content.split() for doc in documents]
        return BM25Okapi(tokenized_docs)

    def initialRetrieval(self):
        all_docs = self.vectorstore.similarity_search("", k=self.vectorstore.index.ntotal)
        bm25 = self.create_bm25_index(all_docs)
        bm25_scores = bm25.get_scores(self.query.split())
        vector_results = self.vectorstore.similarity_search_with_score(self.query, k=len(all_docs))

        vector_scores = np.array([score for _, score in vector_results])
        vector_scores = 1 - (vector_scores - np.min(vector_scores)) / (np.max(vector_scores) - np.min(vector_scores))
        bm25_scores = (bm25_scores - np.min(bm25_scores)) / (np.max(bm25_scores) - np.min(bm25_scores))

        combined_scores = self.alpha * vector_scores + (1 - self.alpha) * bm25_scores
        sorted_indices = np.argsort(combined_scores)[::-1]

        return [all_docs[i] for i in sorted_indices[:self.k]]

    def reRanking(self, initial_docs):
        prompt_template = PromptTemplate(
            input_variables=["query", "doc"],
            template="""On a scale of 1-10, rate the relevance of the following document to the query. Consider the specific context and intent of the query, not just keyword matches.
            Query: {query}
            Document: {doc}

            Please provide only a number between 1 and 10 as the relevance score. Do not include any explanations or additional text.
            Relevance Score:"""
        )
        scored_docs = []
        for doc in initial_docs:
            final_prompt = prompt_template.format(
                query = self.query,
                doc = doc
            )
            score = self.llm(final_prompt)
            print(score)
            try:
                score = float(score)
            except ValueError:
                score = 0  # Default score if parsing fails
            scored_docs.append((doc, score))
            print(f"doc processed")

            print(score)
        
        reranked_docs = sorted(scored_docs, key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in reranked_docs[:self.top_n]]
    
    def samay(self):
        initial_docs = self.initialRetrieval()
        return initial_docs