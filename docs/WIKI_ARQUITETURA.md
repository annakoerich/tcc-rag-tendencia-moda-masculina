# Documentação de Arquitetura e Engenharia de Software (Wiki Oficial)

**Projeto:** Sistema RAG para Apoio à Tomada de Decisão no Varejo de Moda Masculina  
**Autora:** Anna Koerich  
**Instituição:** Centro Universitário Católica de Santa Catarina (Católica SC)  
**Linha de Projeto:** Inteligência Artificial (IA)  
**Semestre:** 2026/2 — 8º Período  

---

## 1. Visão Geral do Sistema

O **Projeto Moda** foi concebido para resolver o problema crítico de aquisição empírica de produtos e acúmulo de estoque parado em pequenas lojas de moda masculina. Através de uma arquitetura baseada em **Retrieval-Augmented Generation (RAG)**, o sistema correlaciona em tempo real relatórios e evidências do mercado da moda com os dados reais de estoque do lojista, gerando recomendações providas de justificativa transparente (*explicabilidade*).

---

## 2. Modelo C4 de Arquitetura

### 2.1 Nível 1: Diagrama de Contexto
Apresenta os usuários do sistema, os limites da solução e suas integrações com o mundo externo.

```mermaid
flowchart TD
    User["Lojista / Gestor de Compras<br/>(Pequeno Varejista de Moda Masculina)"]
    System["Sistema RAG Moda Masculina<br/>[Software System]<br/>Plataforma inteligente de análise de tendências e recomendação de compras"]
    Gemini["Google Gemini AI API<br/>[External System]<br/>Modelos LLM para síntese explicável e briefing executivo"]
    MarketData["Bases de Mercado & Redes<br/>[External Data Source]<br/>WGSN, Pitti Uomo, TikTok Trends, Google Trends"]

    User -->|"Consulta tendências, analisa estoque e solicita recomendações"| System
    System -->|"Envia contexto de mercado e prompt estruturado"| Gemini
    Gemini -->|"Retorna diagnóstico mercadológico em formato JSON"| System
    MarketData -.->|"Relatórios e evidências para indexação vetorial"| System
```

---

### 2.2 Nível 2: Diagrama de Containers
Decompõe o sistema em suas unidades de execução e armazenamento independentes.

```mermaid
flowchart TD
    subgraph ClientApp ["Navegador do Lojista"]
        SPA["Frontend SPA<br/>[React 19 + Vite + Nginx]<br/>Interface de usuário com dashboard de KPIs, assistente RAG e controle de estoque"]
    end

    subgraph CloudServer ["Servidor de Aplicação (Docker / Nuvem)"]
        API["Backend REST API<br/>[FastAPI / Python 3.11]<br/>Fornece rotas CRUD, telemetria de latência e orquestração do motor RAG"]
        RAGCore["Motor RAG & Explicabilidade<br/>[LangChain Core]<br/>Recuperador de similaridade, cruzamento de regras de estoque e sintetizador de resposta"]
    end

    subgraph DataStorage ["Camada de Dados Persistentes"]
        Postgres[("PostgreSQL 16<br/>[Banco Relacional]<br/>Armazena produtos, categorias, níveis de estoque e histórico de recomendações")]
        Chroma[("ChromaDB Persistente<br/>[Banco Vetorial]<br/>Coleção 'tendencias_moda' com embeddings semânticos e metadados de mercado")]
    end

    SPA -->|"Requisições HTTP / JSON (Porta 8000)"| API
    API -->|"Invoca pipeline de recuperação e síntese"| RAGCore
    API -->|"Consultas e persistência via SQLAlchemy ORM"| Postgres
    RAGCore -->|"Busca por similaridade semântica (Top-K)"| Chroma
    RAGCore -->|"Recupera dados de estoque do produto alvo"| Postgres
```

---

### 2.3 Nível 3: Diagrama de Componentes (Backend FastAPI)
Detalha a organização interna dos módulos da API.

```mermaid
flowchart LR
    Router["main.py<br/>(Rotas REST, CORS & Middleware de Latência)"]
    DBLayer["database.py & models.py<br/>(Mapeamento Objeto-Relacional SQLAlchemy)"]
    Schemas["schemas.py<br/>(Validação Pydantic v2 dos contratos JSON)"]
    RAGEngine["rag_engine.py<br/>(Orquestrador RAG, Fallback Heurístico e Integração LLM)"]
    VectorDB["vector_db.py<br/>(Cliente ChromaDB e busca por similaridade)"]

    Router --> Schemas
    Router --> DBLayer
    Router --> RAGEngine
    RAGEngine --> VectorDB
    RAGEngine --> DBLayer
```

---

## 3. Modelo de Dados Relacional (DER)

```mermaid
erDiagram
    PRODUTOS ||--o{ RECOMENDACOES : "gera"
    
    PRODUTOS {
        int id PK
        string nome
        string categoria
        float preco_medio
        float custo_aquisicao
        int quantidade_estoque
        int estoque_minimo
        float tendencia_score
        datetime data_atualizacao
    }

    TENDENCIAS {
        int id PK
        string termo
        string categoria
        float score_relevancia
        string sazonalidade
        string nivel_risco
        text descricao
        string fonte
        datetime data_registro
    }

    RECOMENDACOES {
        int id PK
        int produto_id FK
        string titulo
        string categoria
        string acao_sugerida
        text justificativa
        string nivel_prioridade
        datetime data_criacao
    }
```

---

## 4. Pipeline de Inteligência Artificial & RAG

```mermaid
sequenceDiagram
    autonumber
    actor Lojista
    participant UI as Frontend React
    participant API as FastAPI REST
    participant Chroma as ChromaDB Vetorial
    participant PG as PostgreSQL
    participant LLM as Google Gemini / Heurística

    Lojista->>UI: Digita dúvida (ex.: "Vale a pena comprar camisas de linho?")
    UI->>API: POST /rag/consultar { pergunta, produto_id }
    API->>Chroma: buscar_tendencias_similares(query, n_results=3)
    Chroma-->>API: Retorna top-3 documentos com metadados (score, fonte, sazonalidade)
    opt Produto informado
        API->>PG: Consulta estoque atual vs. estoque mínimo do produto
        PG-->>API: Retorna dados estruturados de estoque
    end
    API->>LLM: Injeta documentos recuperados + estoque + prompt explicável
    LLM-->>API: Retorna diagnóstico, ação recomendada, nível de risco e justificativa
    API->>PG: Salva registro na tabela 'recomendacoes'
    API-->>UI: Retorna JSON estruturado e cabeçalho X-Response-Time-Ms
    UI-->>Lojista: Exibe cards visuais com cores de risco e justificativa fundamentada
```

---

## 5. Núcleo Comum de Engenharia

Em total conformidade com o [Portfólio Directions](file:///C:/Users/annak/Documents/TCC/The-Portfolio-Playbook/directions/portfolio-directions-GERAL.md):

| Requisito do Núcleo | Implementação no Projeto Moda | Status |
| :--- | :--- | :--- |
| **Wiki e Documentação** | Este documento `docs/WIKI_ARQUITETURA.md` integrado ao repositório, com C4 Model e DER. | Concluído |
| **Pipeline de CI/CD** | `.github/workflows/ci.yml` configurado no GitHub Actions executando linters, testes unitários e build do React. | Concluído |
| **Análise Estática de Código** | Ruff configurado no backend (`pyproject.toml`) e Oxlint no frontend React. | Concluído |
| **Monitoramento & Observabilidade** | Middleware de telemetria medindo tempo de resposta em cada requisição (`X-Response-Time-Ms`), logs estruturados e endpoint `/health`. | Concluído |

---

## 6. Instruções de Execução e Deploy

### 6.1 Execução Local com Docker
```bash
# Sobe banco Postgres, backend FastAPI e frontend React
docker compose up --build -d

# Visualização de logs
docker compose logs -f backend
```
- Frontend: `http://localhost:80`
- API Backend: `http://localhost:8000`
- Swagger Interativo: `http://localhost:8000/docs`
- Healthcheck: `http://localhost:8000/health`

### 6.2 Execução sem Docker (Ambiente Virtual)
```bash
# 1. Iniciar Backend
venv\Scripts\uvicorn main:app --reload --port 8000

# 2. Iniciar Frontend
cd frontend
npm run dev
```

### 6.3 Deploy em Nuvem (Azure / AWS / GCP)
Para atender à exigência de ambiente produtivo público e estável:
1. Instanciar uma máquina virtual Linux (Ubuntu 22.04 LTS) na Azure (usando créditos do GitHub Student Pack) ou AWS EC2;
2. Clonar o repositório público do GitHub na máquina remota;
3. Criar o arquivo `.env` com as chaves de produção;
4. Executar `docker compose up -d`.
5. Apontar o IP público ou domínio próprio no pôster técnico (formato A0 com QR Code funcional).
