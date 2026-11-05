# Declaração de Conformidade com LGPD, Ética e Governança de IA

**Projeto:** Sistema RAG para Apoio à Tomada de Decisão no Varejo de Moda Masculina  
**Autora:** Anna Koerich  
**Instituição:** Centro Universitário Católica de Santa Catarina (Católica SC)  
**Linha de Projeto:** Inteligência Artificial (IA)  
**Data:** Novembro de 2026  

---

## 1. Princípios Éticos e Propósito do Sistema

O presente projeto foi desenvolvido com foco exclusivo no suporte à tomada de decisão operacional e estratégica de pequenos e médios lojistas de moda masculina. Sua finalidade é mitigar compras empíricas incorretas, prevenir a imobilização desnecessária de capital de giro e reduzir o descarte de peças não comercializadas.

O sistema atua sob o princípio da **IA Centrada no Humano** (*Human-in-the-Loop*):
- O motor de IA e RAG gera **sugestões e diagnósticos explicáveis**;
- A decisão final de compra, negociação com fornecedores e precificação permanece integralmente sob responsabilidade do gestor lojista;
- O sistema não executa compras automáticas nem impõe decisões de forma autônoma.

---

## 2. Conformidade com a Lei Geral de Proteção de Dados (LGPD - Lei nº 13.709/2018)

Em estrita consonância com a LGPD e o regulamento de normas do Portfólio ([normas.md](file:///C:/Users/annak/Documents/TCC/The-Portfolio-Playbook/documentation/normas.md)):

### 2.1 Minimização e Não Utilização de Dados Pessoais de Clientes Finais
- **O sistema NÃO coleta, NÃO processa e NÃO armazena quaisquer dados pessoais de consumidores finais** (nomes, CPFs, e-mails, endereços, cartões de crédito ou histórico biométrico).
- Os únicos dados manipulados são:
  1. **Dados de Estoque do Lojista:** Nome da peça, categoria, custo médio, preço de venda e quantidade de itens disponíveis;
  2. **Relatórios e Dados de Mercado:** Tendências públicas agregadas, pesquisas abertas do setor têxtil (WGSN, feiras de moda, redes sociais públicas).

### 2.2 Transparência e Explicabilidade do Modelo
- O Artigo 20 da LGPD assegura o direito à revisão de decisões automatizadas.
- O motor RAG deste projeto foi projetado com **arquitetura de explicabilidade**:
  - Cada recomendação retornada pelo assistente inclui obrigatoriamente a citação da **fonte documental recuperada** (ex.: WGSN, Pitti Uomo, TikTok Trends);
  - A justificativa relaciona a métrica de tendência com o número de unidades em estoque do lojista, eliminando o comportamento de "caixa preta" (*black box*).

### 2.3 Segurança da Informação e Armazenamento
- Credenciais e segredos de conexão com banco de dados e APIs de IA são gerenciados por variáveis de ambiente (`.env`), sem exposição no código-fonte público;
- Em ambiente produtivo, o tráfego HTTP é protegido por criptografia TLS/HTTPS;
- As bases vetoriais no ChromaDB contêm exclusivamente textos informativos de domínio público sobre cortes, tecidos e estações do ano.

---

## 3. Mitigação de Vieses e Alucinações no RAG

Para garantir a confiabilidade técnica e a integridade acadêmica:
1. **Redução de Alucinações via RAG:** A IA não gera recomendações com base puramente em conhecimento paramétrico genérico; o modelo é forçado a ancorar sua resposta nos documentos recuperados do banco vetorial ChromaDB.
2. **Fallback Heurístico Resiliente:** Em caso de indisponibilidade da API do LLM ou de ausência de evidências na base de mercado, o sistema aciona um sintetizador determinístico baseado em regras de negócio consolidadas, impedindo a geração de conselhos fabricados.
3. **Avaliação Contínua:** O projeto dispõe de rotina automatizada de testes de recuperação semântica (`test_rag_evaluation.py`) que audita a relevância das respostas e a aderência das fontes.

---

## 4. Declaração de Autoria e Integridade

Em cumprimento ao **Critério 5 (Ética, Integridade e Autoria)** da disciplina de Portfólio, declara-se que todo o código-fonte, modelagem de dados, arquitetura RAG e frontend foram concebidos e implementados de maneira autoral, com rigor técnico e respeito absoluto aos direitos autorais de bibliotecas de terceiros (todas sob licenças permissivas MIT/Apache 2.0).
