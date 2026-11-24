#pip install markdown


from langchain_community.document_loaders import DirectoryLoader , PyPDFLoader
#from langchain_openai import ChatOpenAI

from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama


from langchain_core.prompts import PromptTemplate
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from prompts import qa_system_prompt, contextualize_q_system_prompt
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain.chains import RetrievalQAWithSourcesChain
from langchain_classic.chains import RetrievalQAWithSourcesChain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_classic.chains import RetrievalQA
from dotenv import load_dotenv
load_dotenv()
import os


from flask import Flask, render_template, request

import markdown



#os.environ['OPENAI_API_KEY'] = os.getenv("OPENAI_API_KEY")
#chat history and conversation store will be created once the flask app starts. Chat data will persist as long as the flask session is active.
chat_history = []
conversation_store = {}
FAISS_PATH = "faiss"
#llm = ChatOpenAI(model="gpt-3.5-turbo")

llm = ChatOllama(model="llama3.2:latest")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

app = Flask(__name__)


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in conversation_store:
        print(f"Creating store")
        conversation_store[session_id] = ChatMessageHistory()

    return conversation_store[session_id]


def get_document_loader():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    static_path = os.path.join(base_dir, "scrapping_text/scraped_pdfs")

    print("FULL PATH:", static_path)

    all_files = []
    for root, dirs, files in os.walk(static_path):
        for file in files:
            print("FOUND FILE:", file)
            if file.endswith(".pdf"):
                all_files.append(os.path.join(root, file))

    print("PDF FILES:", all_files)

    docs = []
    for file in all_files:
        loader = PyPDFLoader(file)
        docs.extend(loader.load())

    print(f"Loaded {len(docs)} documents manually")

    return docs

def get_text_chunks(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
        
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

# ORIGINAL IMPLEMENTATION
# def get_embeddings():
#     documents = get_document_loader()
#     chunks = get_text_chunks(documents)
#     db = FAISS.from_documents(
#         chunks, OpenAIEmbeddings()
#     )
    
#     return db

# NEW IMPLEMENTATION - Create embeddings and store in a path
def get_embeddings():
    path = os.path.join(os.getcwd(), FAISS_PATH)
    index_file = os.path.join(path, "index.faiss")

    # Check if actual FAISS file exists
    if os.path.exists(index_file):
        print(f"Index exists. Loading from {path}")
        db = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
    else:
        print(f"Index not found. Creating new index...")

        documents = get_document_loader()


        if not documents:
            raise ValueError("❌ No PDF documents found in 'static/' folder")

        chunks = get_text_chunks(documents)

        if not chunks:
            raise ValueError("❌ Text splitting produced no chunks")
        
        
        chunks = get_text_chunks(documents)

        db = FAISS.from_documents(chunks, embeddings)

        # Ensure directory exists
        os.makedirs(path, exist_ok=True)

        db.save_local(path)
        print(f"Index created and saved at {path}")

    return db

def get_retriever():
    db = get_embeddings()
    retriever = db.as_retriever()
    return retriever


def process_llm_response(chain, question):

    llm_response = chain(question)
    
    print('Sources:')
    for i, source in enumerate(llm_response['source_documents']):
        result = llm_response['result']
        source_document = source.metadata['source']
        page_number = source.metadata['page']
        print(f"page {page_number}")
        source_document = source_document[7:]
        
        return result, source_document, page_number

def get_chain():
    retriever = get_retriever()
        
    chain = RetrievalQA.from_chain_type(llm = llm,
                                        chain_type="stuff",
                                        retriever = retriever,
                                        return_source_documents = True
                                        )
    return chain

# Initialize the FAISS retriever globally once on startup
retriever = get_retriever()

@app.route('/')
def index():
    return render_template('index.html')

    
@app.route('/chat', methods = ['GET', 'POST'])
def document_display():
    '''
    If it is a GET request, load the chat page without any values, if it is a POST request read the question in the request, find the answer and render the chat page with the chat history
    '''

    if request.method == 'GET':
        return render_template('chat.html')
    
    question = request.form['question']

    contextualize_q_prompt = ChatPromptTemplate.from_messages([("system", contextualize_q_system_prompt),MessagesPlaceholder(variable_name="chat_history"),("human", "{input}"),])
    history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
    qa_prompt = ChatPromptTemplate.from_messages([("system", qa_system_prompt),MessagesPlaceholder(variable_name="chat_history"),("human", "{input}"),])
    

    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
    conversational_rag_chain = RunnableWithMessageHistory(rag_chain,get_session_history,input_messages_key="input",history_messages_key="chat_history",output_messages_key="answer")
    response = conversational_rag_chain.invoke({"input": question},config={"configurable": {"session_id": "abc123"}},) #Hardcoding the session_id
    formatted_response = markdown.markdown(response['answer'])
    chat_history.append(question)
    chat_history.append(formatted_response)
    #chat_history.append(response['answer'])

    
    
    return render_template('chat.html', chat_history = chat_history)


if __name__ == "__main__":
    app.run(debug=True)