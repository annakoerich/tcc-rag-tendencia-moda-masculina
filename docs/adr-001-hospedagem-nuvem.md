# ADR 001: Arquitetura de Hospedagem em Nuvem e Orquestração de Contêineres

## Status
Aprovado

## Contexto
O Projeto Moda necessita de um ambiente produtivo na nuvem com alta disponibilidade, estabilidade contínua até o encerramento do semestre letivo (dezembro/2026) e suporte à execução simultânea de:
1. Um banco de dados relacional (PostgreSQL 16) com persistência em disco;
2. Um motor vetorial (ChromaDB) com indexação semântica e embeddings locais (ONNX);
3. Uma API assíncrona em Python (FastAPI) consumindo modelos generativos (Google Gemini);
4. Uma aplicação cliente em React com compilação estática servida sob HTTPS com certificado válido.

Adicionalmente, as diretrizes normativas do Portfólio (Católica SC) impõem restrições contratuais explícitas:
- Proibição de plataformas PaaS que abstraem infraestrutura e bancos gerenciados proprietários (Vercel, Netlify, Render, Firebase);
- Exigência de deploy automatizado via CI/CD (GitHub Actions), vedando deploys manuais por SSH interativo ou FTP;
- Vedação estrita de bancos de dados voláteis ou baseados em arquivos temporários em disco efêmero (SQLite/H2);
- Preferência mandatória por provedores corporativos de nuvem (AWS, Azure, GCP) e orquestração de contêineres via Docker.

## Alternativas Avaliadas

### Alternativa 1: Plataformas PaaS Especializadas (Vercel / Render / Supabase)
- **Vantagens:** Configuração inicial rápida, provisionamento automático de certificados SSL.
- **Desvantagens:** Descumprimento frontal dos critérios de avaliação do Portfólio (veto expresso a partir de 2026/1). Ausência de controle fino sobre o ambiente Linux e dependência de serviços externos para indexação vetorial.
- **Decisão:** Rejeitada por não conformidade normativa.

### Alternativa 2: Azure App Service / Container Apps (Serverless Containers)
- **Vantagens:** Escalabilidade vertical/horizontal sob demanda.
- **Desvantagens:** Custo elevado que consome rapidamente a cota de créditos de estudante ($100), complexidade de montagem de volumes persistentes para ChromaDB e PostgreSQL, e classificação em zona cinzenta pedagógica ("serviços que fazem tudo sozinhos sem domínio técnico sobre o ambiente").
- **Decisão:** Rejeitada por custo e risco de conformidade pedagógica.

### Alternativa 3: Máquina Virtual Linux (Azure VM Standard_B2s) + Docker Compose + Caddy (Selecionada)
- **Vantagens:**
  - **Domínio Integral da Infraestrutura:** Controle completo do sistema operacional (Ubuntu 22.04 LTS), isolamento de rede, gerenciamento de processos e configuração de portas (22, 80, 443).
  - **Orquestração Declarativa:** Todo o ecossistema (`moda_postgres`, `moda_backend`, `moda_frontend`, `moda_proxy`) é definido em `docker-compose.yml`, permitindo paridade total entre os ambientes de desenvolvimento, homologação e produção.
  - **Viabilidade Orçamentária:** A instância `Standard_B2s` (2 vCPUs e 4 GiB de memória) opera dentro de uma faixa mensal de ~$30 a 35, mantendo o sistema ativo e estável sem estourar o crédito de $100 do programa Azure for Students até a banca final.
  - **Segurança e TLS Automático:** Utilização do servidor Caddy integrado ao DNS público da Azure (`*.cloudapp.azure.com`), obtendo certificados TLS/HTTPS emitidos e renovados via Let's Encrypt de forma autônoma.
  - **Deploy Contínuo (CD):** Automação total via GitHub Actions conectando à máquina virtual após a aprovação de todos os linters e testes da suíte de integração.

## Decisão
Adota-se a **Alternativa 3**: Máquina Virtual Ubuntu Server no Microsoft Azure, com provisionamento orquestrado via Docker Compose e esteira automatizada de entrega contínua no GitHub Actions.

## Consequências
- **Positivas:**
  - 100% de aderência às exigências do Portfólio Playbook e pontuação máxima no Critério 4 (Deploy e Infraestrutura).
  - Garantia de que a base vetorial (ChromaDB) e o PostgreSQL compartilham volume persistente em disco gerenciado.
  - Defesa técnica sólida na Prova de Autoria, demonstrando conhecimento em Linux, redes, contêineres e CI/CD.
- **Negativas / Cuidados:**
  - Necessidade de monitoramento de consumo de créditos através de alertas no portal Azure Cost Management.
  - Manutenção de cópias de segurança periódicas dos volumes Docker.
