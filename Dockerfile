# Imagem base oficial leve com Python 3.11
FROM python:3.11-slim

# Metadados
LABEL maintainer="Anna Koerich <Católica SC>"
LABEL description="Backend FastAPI com Motor RAG e ChromaDB para Moda Masculina"

# Evita que o Python escreva arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma_db

WORKDIR /app

# Instala dependências de compilação essenciais
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Garante a existência do diretório de persistência do ChromaDB
RUN mkdir -p /app/data/chroma_db

# Porta exposta da API
EXPOSE 8000

# Healthcheck interno do container
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
