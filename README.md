#  Monitor iNFRA
> **Automação de ponta a ponta: Web Scraping, Inteligência Artificial e Dashboards Executivos.**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://seu-link-aqui.streamlit.app)
[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![Google Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange.svg)](https://deepmind.google/technologies/gemini/)

Este projeto foi desenvolvido para centralizar, monitorar e analisar notícias do setor de infraestrutura brasileira, da agência infra (Energia, Transportes, Saneamento, Mineração, etc). Ele substitui a coleta manual de dados por um fluxo automatizado que utiliza **IA** para criar briefings executivos em tempo real.

---

##  O Problema vs. A Solução

* **O Problema:** O alto volume de publicações diárias no setor tornava inviável o acompanhamento minucioso por parte da diretoria sem uma equipe dedicada exclusivamente à leitura e síntese de pautas. Era necessário ler dezenas de matérias diariamente para compilar relatórios para a diretoria.
* **A Solução:** Desenvolvimento de um pipeline que resolve o gargalo informacional através da triagem cognitiva automatizada. A solução orquestra a varredura em larga escala (Web Scraping) e utiliza o Gemini 2.5 Flash para realizar a síntese estratégica de dezenas de matérias simultaneamente. O sistema não apenas coleta dados, mas realiza o "trabalho pesado" de leitura e correlação, convertendo um volume massivo de dados brutos em um briefing executivo consolidado. Isso elimina a dependência de curadoria manual, garante que nenhum fato crítico seja ignorado e entrega insights em frações de segundo. 

---

##  Tecnologias Utilizadas

| Camada | Ferramentas |
| :--- | :--- |
| **Extração de Dados** | Python, Selenium, WebDriver Manager |
| **Inteligência Artificial** | Google Gemini API (Generative AI) |
| **Interface do Usuário** | Streamlit, Plotly, HTML/CSS personalizado |
| **Banco de Dados** | Excel (OpenPyXL) como storage leve |
| **Automação (CI/CD)** | GitHub Actions (Agendamento via Cron Job) |

---

##  Arquitetura do Sistema



1.  **Coleta (Daily Scraping):** O **GitHub Actions** "acorda" diariamente às 13:50, executa o script em um ambiente Linux virtualizado e utiliza Selenium para capturar novas notícias.
2.  **Processamento com IA:** O conteúdo extraído é enviado para a API do **Google Gemini**, que redige o "Boletim Semanal" em estilo briefing executivo, conectando as pautas mais importantes.
3.  **Entrega:** Os dados são salvos no repositório e o **Streamlit Cloud** atualiza instantaneamente o dashboard.

---

##  Funcionalidades Chave

* **Painel de Notícias Interativo:** Filtros dinâmicos por setor, data e busca por palavras-chave com destaque visual (Highlighter).
* **Visualização de Dados:** Gráficos de volume por categoria e Nuvem de Palavras.
* **Filtro via Gráfico:** UX aprimorada onde clicar em uma categoria no gráfico filtra automaticamente todo o feed de notícias.
* **Briefing IA:** Uma aba exclusiva que apresenta uma análise textual fluida de todos os acontecimentos dos últimos 7 dias.

---

##  Segurança e Boas Práticas

O projeto segue rigorosos padrões de segurança:
* **Secrets Management:** Chaves de API e credenciais sensíveis não estão expostas no código, sendo gerenciadas via `st.secrets` no Streamlit e `GitHub Secrets`.

---

## 👤 Autor

**Thiago Raniery** *Analista de Dados & Cientista de Dados* --- 
*Este projeto é parte do meu portfólio profissional e demonstra competências em Engenharia de Dados, Automação e Inteligência Artificial Aplicada.* 
