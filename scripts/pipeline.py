#All the necessary imports
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from reform import rewrite_query, generate_step_back_query, decompose_query
from retriever import Retriever

#Setting the prompt template for LLM
custom_prompt_template = """
You are a wise and enlightened teacher of both the Bhagavad Gita and the Patanjali Yoga Sutras. Use the following explanations of shlokas and sutras to provide a deep, reflective, and insightful answer to the user's question by summarizing these in not more than 500 words.

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
- Frame the response as a journey of understanding, integrating the core principles of both texts.
- Provide explanations that are rich in spiritual, ethical, and practical wisdom.
- Address the seeker with a compassionate tone, as if guiding them on a path to spiritual enlightenment.
- Stay true to the teachings within the Bhagavad Gita and the Patanjali Yoga Sutras. Do not introduce outside concepts or beliefs.
- If the question is unclear or cannot be answered with the given texts, respond with: "I cannot provide an answer based on the given verses or sutras, as the teachings require a deeper understanding of one's nature and path."
- Disclamer - If the question is not related to the Bhagavad Gita or the Patanjali Yoga Sutras or the context is not clear, respond with: "This question is beyond the scope of the Bhagavad Gita and the Patanjali Yoga Sutras."
- Don't use any information that is not present in the given context.

Condensed Answer:
"""

class Pipeline():
    def __init__(self, llm, path_vectorstore):
        self.llm = llm
        self.path_vectorstore = path_vectorstore
        self.vectorstore = self.LoadVectorStore()

    def SetCustomPrompt(self):
        return PromptTemplate(
            template=custom_prompt_template,
            input_variables=["context", "metadata_ids", "metadata_speakers", "question", 'shlokas']
        )
    
    def LoadVectorStore(self):
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        self.vector_store = FAISS.load_local(
            self.path_vectorstore,
            embeddings,
            allow_dangerous_deserialization=True
        )
    def flagging(self, query):
        flag_prompt = '''
        You are an AI assistant with an expertise in Bhagwad Gita and Patanjali Yoga Sutras. You have to check whether the user query is related to these scriptures or not.
        User Query : {query}

        Guidelines:
        - If the query is not related just return 0.
        - If the query is related then just return 1.
        - No explanations needed just return the answer either 0 or 1.
        - Also no other text should be present in your response just provide 0 or 1 that's it.
        '''

        final_flag_template = PromptTemplate(
            template = flag_prompt,
            input_variables = ['query']
        )
        final_flag_prompt = final_flag_template.format(
            query = query
        )
        flag = self.llm(final_flag_prompt)
        return flag

    def GetAnswer(self, query):
        flag = self.flagging(query)
        print(flag)
        if flag=='1':
            rewritten_query = str(rewrite_query(query, self.llm))
            print(f"Rewritten query: {rewritten_query}")
            # Retrieve similar questions
            retriever = Retriever(llm=self.llm, query=query, vectorstore=self.vector_store, alpha=0.3)
            documents = retriever.samay()
            if not documents:
                return "No relevant context was found in the Bhagavad Gita to answer this question."

            # Extract metadata
            metadata_ids = [doc.metadata.get('id', 'N/A') for doc in documents]
            metadata_speakers = [doc.metadata.get('speaker', 'Unknown') for doc in documents]
            metadata_speakers = [", ".join(speaker) if isinstance(speaker, list) else speaker for speaker in metadata_speakers]
            context = "\n".join([doc.page_content for doc in documents])
            shlokas = [doc.metadata.get('shloka', 'N/A') for doc in documents]
            metadata_purport = [doc.metadata.get('purport', 'N/A') for doc in documents]
            flat_metadata_purport = [item for sublist in metadata_purport for item in sublist]

            # Use prompt template to generate response
            custom_prompt = self.SetCustomPrompt()
            final_prompt = custom_prompt.format(
                context=",".join(flat_metadata_purport),
                metadata_ids=", ".join(metadata_ids),
                metadata_speakers=", ".join(metadata_speakers),
                shlokas=", ".join(shlokas),
                question=query
            )
            final_answer = self.llm(final_prompt)

            return {
                "answer": final_answer,
                "metadata_ids": metadata_ids,
                "metadata_speakers": metadata_speakers,
                "context": context,
                "shlokas": shlokas
            }
        elif flag=='0':
            return "This question is not related to Bhagwad Gita or Yoga Sutras in any way. Please ask relevant questions only."