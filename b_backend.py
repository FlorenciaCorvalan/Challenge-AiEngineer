__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
import chromadb
from chromadb.utils import embedding_functions
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import a_env_vars
import openai
from docx import Document
import uuid
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI


# Archivo DOCX a procesar
archivo_docx = "documento.docx"


# Configuración de la API de OpenAI
if a_env_vars.OPENAI_API_KEY is not None:
    openai.api_key = a_env_vars.OPENAI_API_KEY
    print ("OPENAI_API_KEY configurada")
else:
    print ("OPENAI_API_KEY no encontrada")



client4 = OpenAI(
  api_key=openai.api_key,  # this is also the default, it can be omitted
)

def text_embedding(text):
    response = client4.embeddings.create(model="text-embedding-ada-002", input=text)
    return response.data[0].embedding


def leer_docx_y_dividir_chunks(archivo_docx):
    document = Document(archivo_docx)
    chunks_por_parrafo = []
    for paragraph in document.paragraphs:
        chunks_por_parrafo.append(paragraph.text)
    return chunks_por_parrafo
   
client = chromadb.Client()

embedding_function = OpenAIEmbeddingFunction(api_key=openai.api_key, model_name='text-embedding-ada-002')
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
                api_key=openai.api_key,
                model_name="text-embedding-ada-002"
            )

metadata_options = {
    "hnsw:space": "ip"  # You can change this to "ip" or "cosine" if needed
}

#collection = client.get_or_create_collection(
 #   name="stories", embedding_function=embedding_function)

print(client.list_collections())
document = Document(archivo_docx)
collection = client.get_or_create_collection("cuentos-doc",embedding_function=openai_ef)

archivo_docx = "documento.docx"  # Reemplaza con tu archivo DOCX

docs=leer_docx_y_dividir_chunks(archivo_docx)

docs = list(filter(lambda x: x != '', docs))

print(len(docs))
ids = [str(uuid.uuid1()) for _ in range(len(docs))]
collection.add(
    documents=docs,
    ids=ids
    )



print(client.list_collections())

question = 'de que trata cuento corto?'

vector=text_embedding(question)
print(vector)
results=collection.query(    
    query_embeddings=vector,
    n_results=15,
    include=["documents"]
)

	
res = "\n".join(str(item) for item in results['documents'][0])

prompt=f'```{res}```En base a los datos pasados en  ```, quien es Zara?'

messages = [
        {"role": "system", "content": "Respondes lo que se te pregunta en una sola oración"},
        {"role": "user", "content": prompt}
]
response = client4.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0
)
response_message = response.choices[0].message.content.strip()
print(response_message)