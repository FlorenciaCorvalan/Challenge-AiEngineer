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



print(client.list_collections())


def consulta(message):

    print(client.list_collections())

    collection = client.get_or_create_collection("cuentos-doc",embedding_function=openai_ef)
    docs=leer_docx_y_dividir_chunks(archivo_docx)
    docs = list(filter(lambda x: x != '', docs))
    
    print(len(docs))
    ids = [str(uuid.uuid1()) for _ in range(len(docs))]
    collection.add(
        documents=docs,
        ids=ids
    )

    vector = text_embedding(message)

    results = collection.query(    
        query_embeddings=vector,
        n_results=1,
        include=["documents"]
    )

    relevant_chunk = results['documents'][0]
    prompt = f'```{relevant_chunk}, pregunta del usuario: '+ message
    messages = [
        {"role": "system", "content": """Eres un experto en respoder preguntas del usuario sobre los datos que te envia, responde la pregunta del usuario con las siguientes restricciones: siempre responde exactamente lo mismo a la misma pregunta del usuario, responde en una sola oración, usa el mismo idioma en el que se encuentra redactada la pregunta del usuario (si la pregunta está en ingles responde en ingles), agrega emojis que resumen el contenido , y siempre responde en tercera persona"""},
        {"role": "user", "content": prompt},
        {'role': 'assistant', 'content': ""}
    ]
    
    response = client4.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
        )
    response_message = response.choices[0].message.content.strip()
    print(response_message)
    return response_message