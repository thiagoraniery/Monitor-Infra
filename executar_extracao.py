import pandas as pd
import time
import os
import re
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==============================================================================
# 1. CONFIGURAÇÕES
# ==============================================================================
ARQUIVO_EXCEL = "AgenciaInfra_Historico.xlsx"
SALVAR_A_CADA = 10
# AJUSTE AQUI: Quantos cliques no botão "Carregar Mais" por categoria
QTD_CLIQUES_CARREGAR_MAIS = 1

CATEGORIAS_SITE = {
     "Transporte": "https://agenciainfra.com/blog/category/infratransporte/",
     "Energia": "https://agenciainfra.com/blog/category/infraenergia/",
     "Mineração": "https://agenciainfra.com/blog/category/mineracao/",
     "Oleo_Gas": "https://agenciainfra.com/blog/category/oleo-gas/",
     "Cidades": "https://agenciainfra.com/blog/category/infra-cidades/",
     "Na Transição": "https://agenciainfra.com/blog/category/infra-transicao/",
     "Saneamento": "https://agenciainfra.com/blog/category/infrasaneamento/",
     "Giro": "https://agenciainfra.com/blog/category/giro-infra/",
     "Eventos": "https://agenciainfra.com/blog/category/infraliveventos/"
}

# ==============================================================================
# 2. FUNÇÕES ESPECIALISTAS
# ==============================================================================

def clicar_carregar_mais(driver, quantidade_cliques, categoria):
    """ Rola a página e clica no botão para carregar o histórico """
    print(f"\n⏳ Buscando histórico em {categoria} ({quantidade_cliques} cliques)...")
    for _ in range(quantidade_cliques):
        try:
            # Rola para o fim para o botão carregar
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            wait = WebDriverWait(driver, 8)
            # Busca o botão por texto (independente de maiúsculas)
            botao = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'carregar mais')]")))

            # Clica via JavaScript para evitar erros de elementos sobrepostos
            driver.execute_script("arguments[0].click();", botao)
            time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Fim das notícias ou botão não encontrado em {categoria}: {type(e).__name__}")
            break

def extrair_data_limpa(texto):
    if not texto: return "01/01/2000"
    match = re.search(r'(\d{2}/\d{2}/\d{4})', str(texto))
    return match.group(1) if match else "01/01/2000"

def capturar_detalhes_noticia(driver, link, categoria):
    try:
        driver.get(link)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        titulo = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text.strip()

        data_bruta = ""
        try:
            data_bruta = driver.find_element(By.CLASS_NAME, "datas-noticia-inline").text
        except Exception:
            try:
                data_bruta = driver.find_element(By.CSS_SELECTOR, "span.elementor-icon-list-text, time").text
            except Exception:
                pass

        seletores_texto = [".elementor-widget-theme-post-content p", ".entry-content p"]
        texto_acumulado = []

        for sel in seletores_texto:
            elementos = driver.find_elements(By.CSS_SELECTOR, sel)
            if elementos:
                for el in elementos:
                    if el.text.strip():
                        texto_acumulado.append(el.text.strip())
                break

        conteudo = "\n".join(texto_acumulado) if texto_acumulado else "Texto não encontrado"

        return {
            "Data": extrair_data_limpa(data_bruta),
            "Título": titulo,
            "Link": link,
            "Categoria": categoria,
            "Fonte": "Agência iNFRA",
            "Conteúdo": conteudo
        }
    except Exception as e:
        print(f"   ⚠️ Falha ao capturar {link}: {type(e).__name__}")
        return None

def salvar_progresso(dados_coletados, df_existente):
    """ Une o que foi coletado nesta execução com a base existente, deduplica e salva """
    df_novo = pd.DataFrame(dados_coletados)
    df_final = pd.concat([df_novo, df_existente]).drop_duplicates(subset=['Link'])
    df_final['D_Temp'] = pd.to_datetime(df_final['Data'], format='%d/%m/%Y', errors='coerce')
    df_final = df_final.sort_values(by='D_Temp', ascending=False).drop(columns=['D_Temp'])
    df_final.to_excel(ARQUIVO_EXCEL, sheet_name="Visão Geral", index=False)
    return df_final

# ==============================================================================
# 3. EXECUÇÃO PRINCIPAL
# ==============================================================================
def main():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    dados_coletados = []

    try:
        if os.path.exists(ARQUIVO_EXCEL):
            df_existente = pd.read_excel(ARQUIVO_EXCEL, sheet_name="Visão Geral")
            links_vistos = set(df_existente['Link'].astype(str).tolist())
        else:
            df_existente = pd.DataFrame()
            links_vistos = set()

        count_checkpoint = 0

        for categoria, url_cat in tqdm(CATEGORIAS_SITE.items(), desc="Setores iNFRA"):
            driver.get(url_cat)
            time.sleep(4)

            clicar_carregar_mais(driver, QTD_CLIQUES_CARREGAR_MAIS, categoria)

            links_setor = set()
            try:
                main_container = driver.find_element(By.CSS_SELECTOR, "main, .elementor-posts-container")
                elementos = main_container.find_elements(By.TAG_NAME, "a")
                for el in elementos:
                    l = el.get_attribute("href")
                    if l and "/blog/" in l and "/category/" not in l and l not in links_vistos:
                        links_setor.add(l)
            except Exception as e:
                print(f"   ⚠️ Não encontrei o container de posts em {categoria}: {type(e).__name__}")
                continue

            print(f"🔗 {len(links_setor)} novas notícias para processar em {categoria}")

            for link in links_setor:
                res = capturar_detalhes_noticia(driver, link, categoria)
                if res:
                    dados_coletados.append(res)
                    links_vistos.add(link)
                    count_checkpoint += 1

                    if count_checkpoint >= SALVAR_A_CADA:
                        df_atualizado = salvar_progresso(dados_coletados, df_existente)
                        count_checkpoint = 0
                        print(f"💾 Checkpoint: {len(df_atualizado)} total.")

    finally:
        driver.quit()

    # ==========================================================================
    # 4. SALVAMENTO FINAL
    # ==========================================================================
    if dados_coletados:
        df_final = salvar_progresso(dados_coletados, df_existente)
        print(f"\n✅ Concluído! Total na base: {len(df_final)}")
    else:
        print("\n🙌 Nenhuma novidade encontrada.")


if __name__ == "__main__":
    main()
