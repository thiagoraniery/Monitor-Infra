# Monitor iNFRA

> **Automação de ponta a ponta: Web Scraping e Dashboards Executivos para o setor de infraestrutura brasileira.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://monitor-infra.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Este projeto foi desenvolvido para centralizar, monitorar e analisar notícias do setor de infraestrutura brasileira (Energia, Transportes, Saneamento, Mineração, Óleo & Gás, etc.), publicadas pela Agência iNFRA. Ele substitui a coleta manual de dados por um fluxo automatizado de scraping, entregando um dashboard interativo com análise de tendências setoriais.

> Projeto de portfólio — a coleta de dados não roda mais em agenda fixa; pode ser disparada manualmente pela aba Actions do GitHub sempre que quiser atualizar a base.

---

## O Problema vs. A Solução

- **O Problema:** O alto volume de publicações diárias no setor tornava inviável o acompanhamento minucioso por parte da diretoria sem uma equipe dedicada exclusivamente à leitura e síntese de pautas.
- **A Solução:** Um pipeline que resolve o gargalo informacional através de varredura automatizada (Web Scraping) e consolidação em uma base histórica única, exposta em um dashboard com filtros dinâmicos, indicadores de tendência (variação vs. período anterior, médias móveis) e perfil detalhado por setor.

---

## Tecnologias Utilizadas

| Camada | Ferramentas |
| :--- | :--- |
| **Extração de Dados** | Python, Selenium, WebDriver Manager |
| **Análise de Dados** | Pandas, Plotly, WordCloud |
| **Interface do Usuário** | Streamlit, HTML/CSS personalizado |
| **Banco de Dados** | Excel (OpenPyXL) como storage leve |
| **Automação (CI/CD)** | GitHub Actions (disparo manual) |

---

## Arquitetura do Sistema

1. **Coleta (Scraping):** Um workflow do **GitHub Actions**, disparado manualmente, roda o script de extração em um ambiente Linux virtualizado e usa Selenium para capturar novas notícias por categoria.
2. **Consolidação:** As notícias novas são deduplicadas por link e mescladas à base histórica em Excel.
3. **Entrega:** Os dados são salvos no repositório e o **Streamlit Cloud** atualiza instantaneamente o dashboard.

---

## Funcionalidades Chave

- **Painel de Notícias Interativo:** Filtros dinâmicos por setor, data e busca por palavras-chave com destaque visual (highlighter).
- **Visualização de Dados:** Gráfico de volume por categoria e nuvem de palavras.
- **Filtro via Gráfico:** clicar em uma categoria no gráfico filtra automaticamente todo o feed de notícias.
- **Análise Setorial:** termômetros de tendência (variação vs. período anterior), volume diário com média móvel de 7 dias e perfil histórico por setor.

---

## Segurança e Boas Práticas

- **Secrets Management:** o workflow de automação usa exclusivamente o `GITHUB_TOKEN` padrão do Actions — não há chaves de API de terceiros envolvidas.

---

## 👤 Autor

**Thiago Raniery** — *Analista de Dados & Cientista de Dados*

*Este projeto é parte do meu portfólio profissional e demonstra competências em Engenharia de Dados, Web Scraping e Desenvolvimento de Dashboards.*
