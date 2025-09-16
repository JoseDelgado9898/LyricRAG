'''
Extra steps: 
1. Spotify client and secrets
2. Set OPENAI_API_KEY
3. Install requirements.txt
'''

import os
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.chat_models import init_chat_model
from langchain_core.vectorstores import InMemoryVectorStore
from spotify_client import *


llm = init_chat_model("gpt-4.1-nano", model_provider="openai")

def create_documents(songs):
    docs=[]
    for s in songs:
        doc = Document(
            page_content = s['lyrics'],
            metadata = s['metadata']
        )
        docs.append(doc)
    return docs

def split_documents(docs):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,  # chunk size (characters)
        chunk_overlap=50,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    splitted = text_splitter.split_documents(docs)
    return splitted

def create_vector_store(docs):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vector_store = InMemoryVectorStore(embedding=embeddings)
    document_ids = vector_store.add_documents(documents=docs)
    return vector_store


def retrieve(vector_store, prompt):
    retrieved_docs = vector_store.similarity_search_with_score(prompt)
    for doc in retrieved_docs:
        song_name = doc[0].metadata['name']
        score = doc[1]
        print(f'Song name: {song_name} , score: {score}')
    return retrieved_docs

def generate(vector_store,prompt):

    context = retrieve(vector_store,prompt)
    parsed_context = '''
    Use the provided context to answer the user's questions.
    Only if the answer cannot be derived from the context use your base knowledge.
    Answer concisely
    '''
    for doc in context:
        parsed_context += f'Metadata for document {doc[0].id}: {doc[0].metadata}\n Song lyrics: {doc[0].page_content}\n'
    parsed_context+= f'User question: {prompt}'
    response = llm.invoke(parsed_context).content
    return response
if __name__ == "__main__":

    load_dotenv()
    songs = generate_top_tracks_lyrics('Harry Styles')
    docs = create_documents(songs)
    splitted_docs = split_documents(docs)
    prompt = 'What popular song references being perpetually stuck while running from bullets ?'
    v_s = create_vector_store(splitted_docs)
    response_baseline = llm.invoke(prompt).content
    response_RAG= generate(v_s,prompt)
    
    print(f'Prompt:\n{prompt}')
    print(f'Baseline response\n{response_baseline}')
    print(f'RAG respone\n{response_RAG}')
