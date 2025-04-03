import os
import random
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum

from fastapi import FastAPI, WebSocket, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import aiohttp
from github import Github, GithubIntegration
from transformers import pipeline

# Configuração Inicial
app = FastAPI(title="API Bicho-Papão 🎃", version="0.6.9")
engine = create_engine('sqlite:///tarefas_fantasma.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Modelos Fantasmas 👻
class PrioridadeFantasma(Enum):
    ZUMBI = 1
    VAMPIRO = 2
    LOBISOMEM = 3
    FANTASMA_CHATO = 999

class TarefaFantasma(Base):
    __tablename__ = 'tarefas'
    id = Column(Integer, primary_key=True)
    titulo = Column(String)
    concluida = Column(Boolean, default=False)
    prioridade = Column(Integer)
    criada_em = Column(DateTime, default=datetime.now())
    assombracao = Column(String)

class TarefaRequest(BaseModel):
    titulo: str
    gritos_necessarios: int = 1

# Serviços da API
class ServicoAssombracao:
    def __init__(self):
        self.classificador = pipeline('text-classification', model='nlptown/bert-base-multilingual-uncased-sentiment')
        self.gh_integration = GithubIntegration(
            os.getenv('GH_APP_ID'),
            open('gh_private_key.pem').read()
        )
    
    async def _classificar_urgência(self, texto: str) -> PrioridadeFantasma:
        result = self.classificador(texto)[0]
        score = int(result['label'][0])
        return PrioridadeFantasma.ZUMBI if score > 3 else PrioridadeFantasma.FANTASMA_CHATO
    
    async def _buscar_assombracao_git(self, repo_name: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.github.com/repos/{repo_name}/commits",
                headers={'Authorization': f'token {os.getenv("GH_TOKEN")}'}
            ) as resp:
                commits = await resp.json()
                return random.choice(commits)['commit']['message'] if commits else "Commit sem mensagem... assustador!"

# Endpoints
@app.post("/tarefas/", response_model=Dict)
async def criar_tarefa_assustadora(tarefa: TarefaRequest):
    """Cria uma tarefa com priorização fantasmagórica"""
    session = Session()
    try:
        assombracao = await ServicoAssombracao()._buscar_assombracao_git("usuario/repo_assustador")
        prioridade = await ServicoAssombracao()._classificar_urgência(assombracao)
        
        nova_tarefa = TarefaFantasma(
            titulo=tarefa.titulo,
            prioridade=prioridade.value,
            assombracao=assombracao
        )
        
        session.add(nova_tarefa)
        session.commit()
        return {
            "id": nova_tarefa.id,
            "aviso": f"Tarefa assombrada por: {assombracao}",
            "prioridade": prioridade.name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fantasmas atrapalharam: {str(e)}")
    finally:
        session.close()

@app.websocket("/assombracao/")
async def websocket_assustador(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            resposta = random.choice([
                "Isso é tudo que você consegue? 👻",
                "Já verificou debaixo da cama?",
                "404 Resposta Útil Not Found",
                "Pare de me perturbar, estou ocupado assombrando commits!"
            ])
            await websocket.send_text(f"👹 Bicho-Papão diz: {resposta}")
    except Exception as e:
        print(f"Fantasma desconectado: {str(e)}")

# Inicialização Fantasma
@app.on_event("startup")
async def assombrar():
    Base.metadata.create_all(bind=engine)
    print("""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣤⣤⣤⣤⣤⣶⣦⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⡿⠛⠉⠙⠛⠛⠛⠛⠻⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⠋⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⠈⢻⣿⣿⡄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣸⣿⡏⠀⠀⠀⣠⣶⣾⣿⣿⣿⠿⠿⠿⢿⣿⣿⣿⣄⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠁⠀⠀⢰⣿⣿⣯⠁⠀⠀⠀⠀⠀⠀⠀⠈⠙⢿⣷⡄⠀
⠀⠀⣀⣤⣴⣶⣶⣿⡟⠀⠀⠀⢸⣿⣿⣿⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣷⠀
⠀⢰⣿⡟⠋⠉⣹⣿⡇⠀⠀⠀⠘⣿⣿⣿⣿⣷⣦⣤⣤⣤⣶⣶⣶⣶⣿⣿⣿⠀
⠀⢸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠹⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠃⠀
⠀⣸⣿⡇⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠉⠻⠿⣿⣿⣿⣿⡿⠿⠿⠛⢻⣿⡇⠀⠀
⠀⣿⣿⠁⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣧⠀⠀
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀
⠀⣿⣿⠀⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⠀⠀
⠀⢿⣿⡆⠀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀
⠀⠸⣿⣧⡀⠀⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠃⠀⠀
⠀⠀⠛⢿⣿⣿⣿⣿⣇⠀⠀⠀⠀⠀⣰⣿⣿⣿⣿⣶⣶⣶⣶⣶⣿⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⣽⣿⡏⠁⠀⠀⢸⣿⡇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⠀⠀⠀⣿⣿⡇⠀⢹⣿⡆⠀⠀⠀⣸⣿⠇⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢿⣿⣦⣄⣀⣠⣴⣿⣿⠁⠀⠈⠻⣿⣿⣿⣿⡿⠏⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠛⠻⠿⠿⠿⠿⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    Serviço de Assombração Iniciado! Acesse http://localhost:8000/docs""")

# Para rodar: uvicorn bicho_papao_api:app --reload