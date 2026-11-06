import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from main import app, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_endpoint_raiz(client):
    response = client.get("/")
    assert response.status_code == 200
    dados = response.json()
    assert dados["status"] == "online"
    assert "versao" in dados


def test_endpoint_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    dados = response.json()
    assert dados["status"] == "healthy"
    assert "timestamp" in dados
    assert "X-Response-Time-Ms" in response.headers


def test_crud_produtos(client):
    novo = {
        "nome": "Camisa Linho Off-White",
        "categoria": "Camisas",
        "preco_medio": 189.90,
        "custo_aquisicao": 85.00,
        "quantidade_estoque": 12,
        "estoque_minimo": 5,
        "tendencia_score": 92.0
    }
    res_criar = client.post("/produtos/", json=novo)
    assert res_criar.status_code == 201
    prod_criado = res_criar.json()
    assert prod_criado["id"] is not None
    assert prod_criado["nome"] == novo["nome"]
    prod_id = prod_criado["id"]

    res_listar = client.get("/produtos/")
    assert res_listar.status_code == 200
    lista = res_listar.json()
    assert len(lista) == 1

    res_obter = client.get(f"/produtos/{prod_id}")
    assert res_obter.status_code == 200
    assert res_obter.json()["nome"] == novo["nome"]

    res_atualizar = client.put(f"/produtos/{prod_id}", json={"quantidade_estoque": 20})
    assert res_atualizar.status_code == 200
    assert res_atualizar.json()["quantidade_estoque"] == 20

    res_deletar = client.delete(f"/produtos/{prod_id}")
    assert res_deletar.status_code == 200

    res_busca_deletado = client.get(f"/produtos/{prod_id}")
    assert res_busca_deletado.status_code == 404


def test_dashboard_kpis(client):
    client.post("/produtos/", json={
        "nome": "Calça Jeans Slim",
        "categoria": "Calças",
        "preco_medio": 220.0,
        "custo_aquisicao": 95.0,
        "quantidade_estoque": 2,
        "estoque_minimo": 5,
        "tendencia_score": 70.0
    })

    res = client.get("/dashboard/kpis")
    assert res.status_code == 200
    kpis = res.json()
    assert kpis["total_produtos"] == 1
    assert kpis["produtos_estoque_critico"] == 1
    assert "distribuicao_risco" in kpis
