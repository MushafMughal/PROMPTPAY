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
    Chroma.from_documents(documents=chunks,  embedding=embedding, persist_directory="./rag/promptpay_pdf_sql_chroma_db")

# ingest() #run only first time


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
    #model = ChatOllama(model="llama3.2",temperalture=0)
    model = ChatOllama(model="llama3.2:latest", temperalture=0)
    prompt = PromptTemplate.from_template(
    """
    You are a friendly assistant. Answer the question based only on the following context.
    If the answer cannot be found in the context, say: "No context available for this question."

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