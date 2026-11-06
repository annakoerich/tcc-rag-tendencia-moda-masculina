from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship

from database import Base


class ProdutoModel(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), index=True, nullable=False)
    categoria = Column(String(100), index=True, nullable=False)
    preco_medio = Column(Float, nullable=False, default=0.0)
    custo_aquisicao = Column(Float, nullable=True, default=0.0)
    quantidade_estoque = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=5)
    tendencia_score = Column(Float, nullable=False, default=0.0)
    data_atualizacao = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    recomendacoes = relationship("RecomendacaoModel", back_populates="produto", cascade="all, delete-orphan")


class TendenciaModel(Base):
    __tablename__ = "tendencias"

    id = Column(Integer, primary_key=True, index=True)
    termo = Column(String(150), index=True, nullable=False)
    categoria = Column(String(100), index=True, nullable=False)
    score_relevancia = Column(Float, nullable=False, default=50.0)
    sazonalidade = Column(String(50), nullable=True)
    nivel_risco = Column(String(50), nullable=False, default="Moderado")
    descricao = Column(Text, nullable=True)
    fonte = Column(String(100), nullable=True, default="Análise de Mercado / Redes")
    data_registro = Column(DateTime(timezone=True), server_default=func.now())


class RecomendacaoModel(Base):
    __tablename__ = "recomendacoes"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="SET NULL"), nullable=True)
    titulo = Column(String(200), nullable=False)
    categoria = Column(String(100), nullable=False)
    acao_sugerida = Column(String(100), nullable=False)
    justificativa = Column(Text, nullable=False)
    nivel_prioridade = Column(String(50), nullable=False, default="Média")
    data_criacao = Column(DateTime(timezone=True), server_default=func.now())

    produto = relationship("ProdutoModel", back_populates="recomendacoes")