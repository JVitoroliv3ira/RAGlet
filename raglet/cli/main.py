import os
from typing import List, Dict, Any

import typer
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from openai import OpenAI

app = typer.Typer(help="RAGlet: CLI para análise de projetos via RAG")

def get_chroma_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(path="./raglet_db")

client = get_chroma_client()
embedding_fn = OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small"
)
collection = client.get_or_create_collection(
    name="code_index",
    embedding_function=embedding_fn
)

def parse_simple_python(file_path: str) -> List[str]:
    with open(file_path, "r") as f:
        content = f.read()

    chunks = []
    current_chunk = []
    in_function = False

    for line in content.split('\n'):
        if line.startswith('def ') or line.startswith('class '):
            if current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []
            in_function = True

        if in_function:
            current_chunk.append(line)
        
        if line.strip() == '' and in_function:
            in_function = False

    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks

class OpenAIClient:
    def __init__(self):
        self.client = OpenAI()
    
    def generate_response(self, context: str, question: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que responde perguntas técnicas com base no código fornecido."
                },
                {
                    "role": "user",
                    "content": f"Contexto:\n{context}\n\nPergunta: {question}"
                }
            ]
        )
        return response.choices[0].message.content

@app.command(help="Indexa um projeto no banco vetorial.")
def index(file_path: str = typer.Argument("calculadora.py")) -> None:
    try:
        chunks = parse_simple_python(file_path)
        documents = []
        metadatas: List[Dict[str, Any]] = []
        ids = []

        for idx, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "file": file_path,
                "chunk_id": idx,
                "type": "function" if "def" in chunk else "class"
            })
            ids.append(f"{file_path}_{idx}")

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

        typer.echo(f"✅ Indexados {len(documents)} chunks de {file_path}!")

    except Exception as e:
        typer.secho(f"❌ Erro: {str(e)}", fg="red")

@app.command(help="Pergunta sobre o projeto indexado.")
def ask(question: str) -> None:
    try:
        results = collection.query(
            query_texts=[question],
            n_results=3
        )
        
        context = "\n\n".join(results['documents'][0])
        response = OpenAIClient().generate_response(context, question)
        
        typer.echo("\n🔍 Resposta:")
        typer.echo(response)

    except Exception as e:
        typer.secho(f"❌ Erro: {str(e)}", fg="red")

if __name__ == '__main__':
    app()