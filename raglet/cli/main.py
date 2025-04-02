import typer

app = typer.Typer(help="RAGlet: CLI para análise de projetos via RAG")

@app.command(help="Indexa um projeto no banco vetorial.")
def index() -> None:
    return None

@app.command(help="Pergunta sobre o projeto indexado.")
def ask() -> None:
    return None

if __name__ == '__main__':
    app()
