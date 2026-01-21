from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_groq import ChatGroq

from dotenv import load_dotenv
import requests
load_dotenv()

def tutor_agent(query):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectorstore = FAISS.load_local("faiss_syllabus",embeddings,allow_dangerous_deserialization=True)
    llm = ChatGroq(model="llama-3.3-70b-versatile")

    retriever = vectorstore.as_retriever()
    context = retriever.invoke(query)

    response = llm.invoke(f"""Answer this doubt: {query} using ONLY the following syllabus context:\n{context}\nIf the context does not contain the answer, reply with 'NOT_IN_SYLLABUS'.""")

    if "NOT_IN_SYLLABUS" in response.content:
        print("Not in syllabus....Getting your answer from Wikipedia!")

        try:
            wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

            wiki_context = wikipedia.run(query)

            response = llm.invoke(f"""Syllabus did not mention this topic. Wikipedia content: {wiki_context}\n Generate this wikipedia content ONLY related to the question asked by the user\n User question: {query}""")

            return response.content
    
        
        except (requests.exceptions.RequestException, Exception):
            return (
                "This topic is not covered in the syllabus, "
                "and Wikipedia could not be accessed due to network issues.\n\n"
                "Here is a general explanation based on my knowledge:\n\n"
                + llm.invoke(f"Explain this concept clearly: {query}").content
            )
        
    return response.content