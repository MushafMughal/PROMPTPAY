# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import os
from groq import Groq
client = Groq(api_key="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")

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
    Chroma.from_documents(documents=chunks,  embedding=embedding, persist_directory="rag/sql_chroma_db")

# ingest() #run only first time


def llm_groq(prompt):
    chat_completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        # model="gpt-4o-mini",
        # model="qwen-2.5-32b",
        # model="gemma2-9b-it",
        # model="allam-2-7b",
        # model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a fast and efficient assistant."},
            {"role": "user", "content": str(prompt)},
        ],
    )
    return chat_completion.choices[0].message.content


def rag_chain():

    # llm = ChatOllama(
    #     model="qwen2.5:14b-instruct-q6_K",
    #     temperature=0,
    #     base_url="http://192.168.18.86:11434"
    # )

    prompt = PromptTemplate.from_template(
        """
        <s> [Instructions] You are a friendly assistant. Answer the question based only on the following context. 
        If you don't know the answer, then reply, No Context availabel for this question {input}. [/Instructions] </s> 
        [Instructions] Question: {input} 
        Context: {context} 
        Answer: [/Instructions]
        """
    )
    #Load vector store
    embedding = FastEmbedEmbeddings()
    vector_store = Chroma(persist_directory="rag/sql_chroma_db", embedding_function=embedding)

    #Create chain
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={
            "k": 3,
            "score_threshold": 0.5,
        },
    )

    document_chain = create_stuff_documents_chain(llm_groq, prompt)
    chain = create_retrieval_chain(retriever, document_chain)

    return chain