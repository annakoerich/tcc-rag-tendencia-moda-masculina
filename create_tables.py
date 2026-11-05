from database import Base, engine

print("Recriando tabelas no banco de dados PostgreSQL...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Tabelas criadas com sucesso: produtos, tendencias, recomendacoes!")
