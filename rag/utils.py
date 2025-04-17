# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import ChatOllama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import os
from groq import Groq
from google import genai
from google.genai import types
gclient = genai.Client(api_key="AIzaSyCxPjOUifGIh84uiCAp0KKFD7zJ1zTV-pU")
client = Groq(api_key="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")

# system_prompt = """You are given a question and a context. Answer the question **only if** the context clearly and directly supports it.

# **INSTRUCTIONS:**
# - Do NOT make assumptions, guesses, or inferred answers.
# - If the context does NOT explicitly contain the information needed to answer, respond with:
#   `No context available for this question.`

# - If the question is a greeting (e.g., "hi", "hello", "hey") or a meta-question (e.g., "what can you do?", "who are you?", "tell me about yourself"), respond with:
#   `I'm a RAG bot from PromptPay, created to help you with FAQ queries related to the PromptPay banking app. Ask me anything about it!`  

# - Otherwise, if the context is missing, unrelated, or insufficient, always respond:
#   `No context available for this question.`

# - Your response must ONLY contain the final answer string. No explanation, formatting, or extra text.

# **PERFORM NOW ON THESE:**
# """

def ingest():
    # Get the doc
    loader = PyPDFLoader("rag/assets/User Manual.pdf")
    pages = loader.load_and_split()
    # Split the pages by char
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
        separators=["\n\n"],
    )

    chunks = text_splitter.split_documents(pages)
    print(f"Split {len(pages)} documents into {len(chunks)} chunks.")
    #
    embedding = FastEmbedEmbeddings()
    #Create vector store
    Chroma.from_documents(documents=chunks,  embedding=embedding, persist_directory="./rag/promptpay_pdf_sql_chroma_db")

# ingest() #run only first time

def call_llm(prompt):

    response = gclient.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction="You are a fast and efficient assistant.",),
        contents=prompt
    )

    return response.text

def llm(prompt):
    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a fast and efficient assistant."},
            {"role": "user", "content": str(prompt)},
        ],
    )
    return chat_completion.choices[0].message.content


def rag_chain():
    prompt = PromptTemplate.from_template(
        """
        You are a friendly assistant. Answer the question based only on the following context. 
        If you don't know the answer, then reply, No Context availabel for this question. 
        
        Question: {input} 
        Context: {context} 
        Answer:
        """
    )
    #Load vector store
    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(persist_directory="./rag/promptpay_pdf_sql_chroma_db", embedding_function=embedding)

    #Create chain
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 3,
            "score_threshold": 0.5,
        },
    )

    document_chain = create_stuff_documents_chain(llm, prompt)
    chain = create_retrieval_chain(retriever, document_chain)

    return chain

