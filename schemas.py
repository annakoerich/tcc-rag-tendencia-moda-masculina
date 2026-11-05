from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ============================
# Schemas para Produtos
# ============================
class ProdutoBase(BaseModel):
    nome: str = Field(..., example="Camisa de Linho Manga Curta")
    categoria: str = Field(..., example="Camisas")
    preco_medio: float = Field(..., ge=0.0, example=189.90)
    custo_aquisicao: Optional[float] = Field(0.0, ge=0.0, example=85.00)
    quantidade_estoque: int = Field(0, ge=0, example=15)
    estoque_minimo: int = Field(5, ge=0, example=5)
    tendencia_score: float = Field(0.0, ge=0.0, le=100.0, example=85.5)

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    categoria: Optional[str] = None
    preco_medio: Optional[float] = None
    custo_aquisicao: Optional[float] = None
    quantidade_estoque: Optional[int] = None
    estoque_minimo: Optional[int] = None
    tendencia_score: Optional[float] = None

class ProdutoResponse(ProdutoBase):
    id: int
    data_atualizacao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================
# Schemas para Tendências
# ============================
class TendenciaBase(BaseModel):
    termo: str = Field(..., example="Calça Wide Leg")
    categoria: str = Field(..., example="Calças")
    score_relevancia: float = Field(50.0, ge=0.0, le=100.0, example=92.0)
    sazonalidade: Optional[str] = Field("Atemporal", example="Primavera/Verão")
    nivel_risco: str = Field("Moderado", example="Baixo")
    descricao: Optional[str] = Field(None, example="Alta busca por modelagens amplas em redes sociais.")
    fonte: Optional[str] = Field("Análise de Mercado / Redes", example="Instagram / Google Trends")

class TendenciaCreate(TendenciaBase):
    pass

class TendenciaResponse(TendenciaBase):
    id: int
    data_registro: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================
# Schemas para Recomendações (RAG)
# ============================
class RecomendacaoBase(BaseModel):
    produto_id: Optional[int] = None
    titulo: str = Field(..., example="Oportunidade: Reforço em Peças de Linho")
    categoria: str = Field(..., example="Camisas")
    acao_sugerida: str = Field(..., example="Aumentar Pedido")
    justificativa: str = Field(..., example="A busca por peças de linho cresceu 40% nas plataformas digitais e o estoque atual está próximo do mínimo.")
    nivel_prioridade: str = Field("Média", example="Alta")

class RecomendacaoCreate(RecomendacaoBase):
    pass

class RecomendacaoResponse(RecomendacaoBase):
    id: int
    data_criacao: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ============================
# Schemas para Consulta RAG & Dashboard
# ============================
class ConsultaRAGRequest(BaseModel):
    pergunta: str = Field(..., example="Devo aumentar o estoque de jaquetas de couro para o inverno?")
    categoria: Optional[str] = Field(None, example="Jaquetas")
    produto_id: Optional[int] = Field(None, example=1)

class ConsultaRAGResponse(BaseModel):
    pergunta: str
    diagnostico: str
    acao_recomendada: str
    nivel_risco: str
    justificativa_explicavel: str
    fontes_consultadas: List[str] = []
    recomendacao_id: Optional[int] = None

class GerarTendenciasIARequest(BaseModel):
    tema: Optional[str] = Field("Tendências de Moda Masculina Atual", example="Alfaiataria Moderna e Casual Chic")

