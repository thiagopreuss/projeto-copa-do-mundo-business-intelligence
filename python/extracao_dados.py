import customtkinter as ctk
from tkinter import messagebox
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from io import StringIO
import time
import re
import os



# Dicionário Global para armazenar os dados coletados
estado = {
    "links_jogos":[],
    "rodada": None,
    "quant_jogos": None,
    "lista_time_casa": [],
    "lista_time_fora": []
}


# Função Buscar Links:
def buscar_links_jogos():

    # Configuração do Selenium para abrir o navegador em modo headless
    #options = Options()
    #options.add_argument("--headless")

    # Cria navegador no modo Headless
    navegador = webdriver.Chrome()

    # Página inicial
    url_stats = "https://optaplayerstats.statsperform.com/pt_BR/soccer/copa-do-mundo-2026-canada-mexico-usa/873cbl9cd9butm4air0mugxzo/opta-player-stats"
    navegador.get(url_stats)

    # Espera o navegador carregar o elemento
    WebDriverWait(navegador, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="Opta_0"]/div/div[1]/div/table')))

    # Encontra todas as linhas da tabela
    linhas = navegador.find_elements(By.XPATH, '//*[@id="Opta_0"]//table/tbody/tr')

    links_jogos = []
    lista_time_casa = []
    lista_time_fora = []

    # Quantidade de Jogos que eu quero buscar o link
    quant_jogos = int(entrada_jogos.get())
    rodada = int(entrada_rodada.get())

    if quant_jogos == "" or rodada == "":
        messagebox.showwarning("Aviso", "Todos os campos devem ser preenchidos antes de buscar os links!")
        return

    for linha in linhas:
        if len(links_jogos) == quant_jogos:   # Quantidade de links que eu quero
            break
        try:
            link = linha.find_element(By.XPATH, './td[2]/a')
            links_jogos.append(link.get_attribute("href"))

        except:
            pass

    for linha in linhas:
        if len(lista_time_casa) == quant_jogos:   # Quantidade de links que eu quero
            break
        try:
            elemento_casa = linha.find_element(By.XPATH, './td[2]').text
            elemento_fora = linha.find_element(By.XPATH, './td[8]').text

            lista_time_casa.append(elemento_casa)
            lista_time_fora.append(elemento_fora)

        except:
            pass

    navegador.quit()

    texto_confrontos = "Links obtidos referentes aos seguintes jogos:\n\n"
    for i in range(len(lista_time_casa)):
        texto_confrontos += f'{lista_time_casa[i]} x {lista_time_fora[i]}\n\n'

    resultado_textbox.insert("1.0",texto_confrontos)

    # Salva os dados no dicionário global "estado"
    estado["links_jogos"] = links_jogos
    estado["rodada"] = rodada
    estado["quant_jogos"] = quant_jogos
    estado["lista_time_casa"] = lista_time_casa
    estado["lista_time_fora"] = lista_time_fora

    # Habilita o botão Extrair Dados
    botao_extrair_dados.configure(state="normal")


# Função Limpar Campos:
def limpar_campos():
    entrada_jogos.delete(0, "end")
    entrada_rodada.delete(0, "end")
    resultado_textbox.delete("1.0", "end")

def converter_contagem_inteira(valor):
    if pd.isna(valor):
        return 0

    texto = str(valor).strip()

    texto = texto.replace('\xa0', '')
    texto = texto.replace(' ', '')
    texto = texto.replace(',', '.')

    if texto in ['', '-', 'nan', 'None']:
        return 0

    try:
        return int(round(float(texto)))
    except:
        print(f"[WARN] Não consegui converter valor de contagem: {repr(valor)}")
        return 0

# Função Extrair Dados:
def extrair_dados():

    # Criação de função de limpeza dos nomes dos times
    def limpar_nome_time(nome):
        substituicoes = {
            "CA Mineiro": "Atlético Mineiro",
            "SC do Recife": "Sport"
        }
        if nome in substituicoes:
            return substituicoes[nome]

        nome = re.sub(r'^(SC|SE|CR|EC|FC|CA|FR|Red Bull)\s+', '', nome, flags=re.IGNORECASE)
        nome = re.sub(r'\s+(SC|CR|EC|FC|CA|FR|Paulista|FC Sao Paulo|FB Porto Alegrense|da Gama)$', ' ', nome,
                      flags=re.IGNORECASE)
        return nome.strip()

    #Pegar tabela ativa

    def pegar_html_tabela_ativa(navegador, wait, contexto, qtd_colunas_esperada=None):
        """
        Procura a tabela correta da aba/time selecionado.

        Se qtd_colunas_esperada for informada, ela só aceita uma tabela
        que tenha exatamente essa quantidade de colunas.
        """

        wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        seletores = [
            ".Opta-On table",
            "li.Opta-On table",
            "table"
        ]

        candidatos = []

        for seletor in seletores:
            elementos = navegador.find_elements(By.CSS_SELECTOR, seletor)

            for elemento in elementos:
                if elemento.is_displayed() and elemento not in candidatos:
                    candidatos.append(elemento)

        print(f"\n[DEBUG] {contexto}")
        print(f"[DEBUG] URL atual: {navegador.current_url}")
        print(f"[DEBUG] Total de tabelas candidatas visíveis: {len(candidatos)}")

        tabelas_lidas = []

        for i, elemento in enumerate(candidatos):
            html = elemento.get_attribute("outerHTML")

            try:
                df_teste = pd.read_html(StringIO(html))[0]
                qtd_colunas = df_teste.shape[1]

                tabelas_lidas.append((i, qtd_colunas, df_teste.shape))

                print(f"[DEBUG] Tabela candidata {i}: {df_teste.shape}")

                if qtd_colunas_esperada is None or qtd_colunas == qtd_colunas_esperada:
                    print(f"[OK] Tabela escolhida no contexto {contexto}: candidata {i}, com {qtd_colunas} colunas")
                    return html

            except Exception as erro:
                print(f"[DEBUG] Tabela candidata {i}: erro ao ler com pandas -> {erro}")

        nome_arquivo = contexto.replace(" ", "_").replace("/", "_").replace("-", "_")

        navegador.save_screenshot(f"debug_{nome_arquivo}.png")

        with open(f"debug_{nome_arquivo}.html", "w", encoding="utf-8") as arquivo:
            arquivo.write(navegador.page_source)

        print(f"\n[ERRO] Não encontrei tabela compatível no contexto: {contexto}")
        print(f"[ERRO] Colunas esperadas: {qtd_colunas_esperada}")
        print(f"[ERRO] Tabelas lidas: {tabelas_lidas}")

        raise Exception(f"Não foi possível encontrar tabela compatível: {contexto}")

    #Função clicar por texto

    def clicar_por_texto(navegador, wait, texto_procurado, contexto):
        """
        Clica em um elemento pelo texto visível.
        Primeiro tenta a/button.
        Se não encontrar, tenta outros elementos como span, li e div.
        """

        texto_procurado = texto_procurado.strip()

        def texto_ok(texto_elemento, texto_procurado):
            texto_elemento = texto_elemento.strip()

            if not texto_elemento:
                return False

            return (
                texto_elemento == texto_procurado
                or texto_procurado in texto_elemento
                or texto_elemento in texto_procurado
            )

        # Tenta por até 10 segundos
        for tentativa in range(20):

            # Tentativa 1: links e botões
            elementos = navegador.find_elements(By.CSS_SELECTOR, "a, button")

            for elemento in elementos:
                texto_elemento = elemento.text.strip()

                if elemento.is_displayed() and texto_ok(texto_elemento, texto_procurado):
                    navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                    time.sleep(0.3)
                    navegador.execute_script("arguments[0].click();", elemento)
                    time.sleep(1)
                    print(f"[OK] Cliquei em '{texto_elemento}' no contexto: {contexto}")
                    return elemento

            # Tentativa 2: outros elementos que podem conter texto clicável
            elementos = navegador.find_elements(By.CSS_SELECTOR, "li, span, div")

            for elemento in elementos:
                texto_elemento = elemento.text.strip()

                # Evita clicar em blocos enormes da página
                if len(texto_elemento) > 60:
                    continue

                if elemento.is_displayed() and texto_ok(texto_elemento, texto_procurado):
                    navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                    time.sleep(0.3)
                    navegador.execute_script("arguments[0].click();", elemento)
                    time.sleep(1)
                    print(f"[OK] Cliquei em '{texto_elemento}' por fallback no contexto: {contexto}")
                    return elemento

            time.sleep(0.5)

        print(f"\n[ERRO] Não encontrei o texto '{texto_procurado}' no contexto: {contexto}")
        print("[DEBUG] URL atual:", navegador.current_url)
        print("[DEBUG] Textos disponíveis em links/botões:")

        elementos_debug = navegador.find_elements(By.CSS_SELECTOR, "a, button, li, span")

        for i, elemento in enumerate(elementos_debug):
            texto_elemento = elemento.text.strip()
            if texto_elemento and len(texto_elemento) <= 80:
                print(i, repr(texto_elemento))

        raise Exception(f"Não encontrei elemento com texto '{texto_procurado}' no contexto: {contexto}")

    #Função clicar_full_game_match_summary

    def clicar_full_game_match_summary(navegador, contexto):
        """
        Clica no botão Full Game dentro da aba Match Summary.
        Se o botão não existir, segue normalmente sem quebrar o script.
        """

        textos_possiveis = ["full game", "jogo completo", "partida completa"]

        time.sleep(0.8)

        # Primeiro tenta encontrar sem mexer muito na página
        elementos = navegador.find_elements(By.CSS_SELECTOR, "button, a, span, div")

        for elemento in elementos:
            try:
                texto_elemento = elemento.text.strip()
                texto_lower = texto_elemento.lower()

                if not texto_elemento or len(texto_elemento) > 80:
                    continue

                if any(texto in texto_lower for texto in textos_possiveis):
                    if elemento.is_displayed():
                        navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                        time.sleep(0.3)
                        navegador.execute_script("arguments[0].click();", elemento)
                        time.sleep(1)

                        # Volta para o topo para os botões dos times aparecerem de novo
                        navegador.execute_script("window.scrollTo(0, 0);")
                        time.sleep(0.8)

                        print(f"[OK] Cliquei em Full Game no contexto: {contexto}")
                        return True

            except:
                continue

        # Se não achou, tenta rolar para baixo e procurar de novo
        navegador.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.8)

        elementos = navegador.find_elements(By.CSS_SELECTOR, "button, a, span, div")

        for elemento in elementos:
            try:
                texto_elemento = elemento.text.strip()
                texto_lower = texto_elemento.lower()

                if not texto_elemento or len(texto_elemento) > 80:
                    continue

                if any(texto in texto_lower for texto in textos_possiveis):
                    if elemento.is_displayed():
                        navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
                        time.sleep(0.3)
                        navegador.execute_script("arguments[0].click();", elemento)
                        time.sleep(1)

                        # Volta para o topo para os botões dos times aparecerem de novo
                        navegador.execute_script("window.scrollTo(0, 0);")
                        time.sleep(0.8)

                        print(f"[OK] Cliquei em Full Game no contexto: {contexto}")
                        return True

            except:
                continue

        print(f"[INFO] Botão Full Game não encontrado no contexto: {contexto}. Seguindo sem clicar.")
        return False

    #Função clicar botão estatísticas na aba Opta Points

    def clicar_botao_estatisticas_opta(navegador, wait):
        """
        Clica no botão Estatísticas dentro da aba Opta Points.
        Rola a tela para baixo e espera o botão aparecer no DOM.
        """

        # Garante que a aba Opta Points carregou de verdade
        wait.until(lambda driver: "/opta-points" in driver.current_url)

        # Rola para baixo para o botão ficar visível
        navegador.execute_script("window.scrollBy(0, 500);")
        time.sleep(0.8)

        # Tenta encontrar o botão por alguns segundos
        for tentativa in range(30):
            botoes_stats = navegador.find_elements(By.CSS_SELECTOR, "button[value='stats']")

            if botoes_stats:
                botao = botoes_stats[0]

                navegador.execute_script("arguments[0].scrollIntoView({block: 'center'});", botao)
                time.sleep(0.3)

                navegador.execute_script("arguments[0].click();", botao)
                time.sleep(1)

                print("[OK] Cliquei no botão Estatísticas usando button[value='stats']")
                return

            # Enquanto não acha, continua rolando um pouco e esperando
            navegador.execute_script("window.scrollBy(0, 150);")
            time.sleep(0.3)

        print("[ERRO] Não encontrei o botão Estatísticas após aguardar.")
        print("[DEBUG] URL atual:", navegador.current_url)
        print("[DEBUG] Quantidade de botões:", len(navegador.find_elements(By.TAG_NAME, "button")))

        raise Exception("Não encontrei o botão Estatísticas dentro da aba Opta Points")

    # Extração dos dados de cada URL selecionada

    rodada = estado["rodada"]
    links_jogos = estado["links_jogos"]
    lista_time_casa = estado["lista_time_casa"]
    lista_time_fora = estado["lista_time_fora"]

    # Abrindo o Navegador
    navegador = webdriver.Chrome()
    wait = WebDriverWait(navegador, 20)

    df_total_MS = []
    df_total_OP = []
    df_total_MD = []

    for indice, l in enumerate(links_jogos):
        navegador.get(l)
        navegador.maximize_window()
        time.sleep(5)

        nome_time_casa = lista_time_casa[indice]
        nome_time_fora = lista_time_fora[indice]

        print(f"\n[INFO] Extraindo jogo: {nome_time_casa} x {nome_time_fora}")

        # Aba Match Summary:

        # Encontra o elemento do botão para selecionar o time da casa na aba Match Summary
        clicar_por_texto(navegador, wait, nome_time_casa, "Match Summary - Casa")

        # Clica no botão full game embaixo na tela para pegar dados dos jogos caso haja prorrogação
        clicar_full_game_match_summary(navegador, "Match Summary - Casa")

        # Extração de dados html do time casa
        html_casa_MS = pegar_html_tabela_ativa(navegador, wait, "Match Summary - Casa", 16)

        # Encontra o elemento do botão para selecionar o time de fora na aba Match Summary
        clicar_por_texto(navegador, wait, nome_time_fora, "Match Summary - Fora")

        # Extração de dados html do time fora
        html_fora_MS = pegar_html_tabela_ativa(navegador, wait, "Match Summary - Fora", 16)

        # Parsear o contéudo html_casa_MS com o Beautiful Soup
        soup_casa_MS = BeautifulSoup(html_casa_MS, 'html.parser')
        tabela_casa_MS = soup_casa_MS.find(name='table')

        # Parsear o contéudo html_fora_MS com o Beautiful Soup
        soup_fora_MS = BeautifulSoup(html_fora_MS, 'html.parser')
        tabela_fora_MS = soup_fora_MS.find(name='table')

        # Estruturar conteúdos em data frame_casa - Pandas
        df_casa_MS = pd.read_html(StringIO(str(tabela_casa_MS)))[0]  # Faz a leitura do html parseado e estrutura num dataframe
        df_casa_MS = df_casa_MS.iloc[:-1]  # Retira a linha com o total
        df_casa_MS.columns = ['Jogador', 'Gols', 'Assistências', 'Cartões Vermelhos', 'Cartões Amarelos',
                              'Escanteios a favor', 'Chutes', 'Chutes a Gol', 'Chutes Bloqueados', 'Passes',
                              'Cruzamentos', 'Desarmes', 'Impedimentos', 'Faltas Cometidas', 'Faltas Sofridas',
                              'Defesas']  # Renomeia as colunas

        # Acrescentando colunas
        df_casa_MS['Time'] = nome_time_casa
        df_casa_MS['Adversário'] = nome_time_fora
        df_casa_MS['Rodada'] = rodada
        df_casa_MS['Local'] = 'Casa'

        # Aplicando função de limpeza dos nomes dos times no df_casa
        df_casa_MS['Time'] = df_casa_MS['Time'].apply(limpar_nome_time)
        df_casa_MS['Adversário'] = df_casa_MS['Adversário'].apply(limpar_nome_time)

        # Estruturar conteúdo em data frame_fora - Pandas
        df_fora_MS = pd.read_html(StringIO(str(tabela_fora_MS)))[0]
        df_fora_MS = df_fora_MS.iloc[:-1]
        df_fora_MS.columns = ['Jogador', 'Gols', 'Assistências', 'Cartões Vermelhos', 'Cartões Amarelos',
                              'Escanteios a favor', 'Chutes', 'Chutes a Gol', 'Chutes Bloqueados', 'Passes',
                              'Cruzamentos', 'Desarmes', 'Impedimentos', 'Faltas Cometidas', 'Faltas Sofridas',
                              'Defesas']  # Renomeia as colunas

        # Acrescentando colunas no df_fora
        df_fora_MS['Time'] = nome_time_fora
        df_fora_MS['Adversário'] = nome_time_casa
        df_fora_MS['Rodada'] = rodada
        df_fora_MS['Local'] = 'Fora'

        # Aplicando função de limpeza dos nomes dos times no df_fora
        df_fora_MS['Time'] = df_fora_MS['Time'].apply(limpar_nome_time)
        df_fora_MS['Adversário'] = df_fora_MS['Adversário'].apply(limpar_nome_time)

        # Juntando os data frames df_casa e df_fora e transformando em uma lista
        df_final_MS = pd.concat([df_casa_MS, df_fora_MS], ignore_index=True)
        df_total_MS.append(df_final_MS)

        # Aba Opta Points:

        # Mudança para aba Opta Points
        clicar_por_texto(navegador, wait, "OPTA POINTS", "Aba Opta Points")

        # Encontra o elemento do botão para selecionar as estatísticas
        clicar_botao_estatisticas_opta(navegador, wait)

        # Encontra o elemento do botão para selecionar o time de casa na aba Opta Points
        clicar_por_texto(navegador, wait, nome_time_casa, "Opta Points - Casa")

        # Extração de dados html do time casa
        html_casa_OP = pegar_html_tabela_ativa(navegador, wait, "Opta Points - Casa", 24)

        # Encontra o elemento do botão para selecionar o time de fora na aba Opta Points
        clicar_por_texto(navegador, wait, nome_time_fora, "Opta Points - Fora")

        # Extração de dados html do time fora
        html_fora_OP = pegar_html_tabela_ativa(navegador, wait, "Opta Points - Fora", 24)

        # Parsear o contéudo html_casa_OP com o Beautiful Soup
        soup_casa_OP = BeautifulSoup(html_casa_OP, 'html.parser')
        tabela_casa_OP = soup_casa_OP.find(name='table')

        # Parsear o contéudo html_fora_OP com o Beautiful Soup
        soup_fora_OP = BeautifulSoup(html_fora_OP, 'html.parser')
        tabela_fora_OP = soup_fora_OP.find(name='table')

        # Estruturar conteúdos em data frame_casa - Pandas
        df_casa_OP_full = pd.read_html(
            StringIO(str(tabela_casa_OP)),
            decimal='.',
            thousands=None
        )[0]

        # Converte as estatísticas que são contagens para números inteiros
        coluna_jogador_OP = df_casa_OP_full.columns[0]

        print("\n[DEBUG] Colunas Opta Points Casa:")
        print(list(df_casa_OP_full.columns))

        print("\n[DEBUG] ANTES da conversão - Opta Points Casa:")
        print(df_casa_OP_full[[coluna_jogador_OP, 'GC', 'INT', 'PSAV']].to_string())

        colunas_inteiras_OP = ['GC', 'INT', 'PSAV']

        for coluna in colunas_inteiras_OP:
            df_casa_OP_full[coluna] = df_casa_OP_full[coluna].apply(converter_contagem_inteira)

        print("\n[DEBUG] DEPOIS da conversão - Opta Points Casa:")
        print(df_casa_OP_full[[coluna_jogador_OP, 'GC', 'INT', 'PSAV']].to_string())


        df_casa_OP = df_casa_OP_full[[coluna_jogador_OP, 'MP', 'GC', 'INT', 'PSAV']].copy()
        df_casa_OP.columns = ['Jogador', 'Minutos Jogados', 'Gols Contra', 'Interceptações',
                              'Penâltis Def.']

        # Separando a coluna Jogador em Jogador e Status do Jogador
        df_casa_OP[['Status do Jogador', 'Jogador']] = df_casa_OP['Jogador'].str.split(' ', n=1, expand=True)
        colunas_casa = [col for col in df_casa_OP.columns if col != 'Status do Jogador'] + ['Status do Jogador']
        df_casa_OP = df_casa_OP[colunas_casa]

        # Acrescentando colunas
        df_casa_OP['Time'] = nome_time_casa
        df_casa_OP['Adversário'] = nome_time_fora
        df_casa_OP['Rodada'] = rodada

        # Aplicando função de limpeza dos nomes dos times no df_casa
        df_casa_OP['Time'] = df_casa_OP['Time'].apply(limpar_nome_time)
        df_casa_OP['Adversário'] = df_casa_OP['Adversário'].apply(limpar_nome_time)

        # Estruturar conteúdo em data frame_fora - Pandas
        df_fora_OP_full = pd.read_html(
            StringIO(str(tabela_fora_OP)),
            decimal='.',
            thousands=None
        )[0]

        # Converte as estatísticas que são contagens para números inteiros
        coluna_jogador_OP = df_fora_OP_full.columns[0]

        print("\n[DEBUG] Colunas Opta Points Fora:")
        print(list(df_fora_OP_full.columns))

        print("\n[DEBUG] ANTES da conversão - Opta Points Fora:")
        print(df_fora_OP_full[[coluna_jogador_OP, 'GC', 'INT', 'PSAV']].to_string())

        colunas_inteiras_OP = ['GC', 'INT', 'PSAV']

        for coluna in colunas_inteiras_OP:
            df_fora_OP_full[coluna] = df_fora_OP_full[coluna].apply(converter_contagem_inteira)

        print("\n[DEBUG] DEPOIS da conversão - Opta Points Fora:")
        print(df_fora_OP_full[[coluna_jogador_OP, 'GC', 'INT', 'PSAV']].to_string())


        df_fora_OP = df_fora_OP_full[[coluna_jogador_OP, 'MP', 'GC', 'INT', 'PSAV']].copy()
        df_fora_OP.columns = ['Jogador', 'Minutos Jogados', 'Gols Contra', 'Interceptações',
                              'Penâltis Def.']

        # Separando a coluna Jogador em Jogador e Status do Jogador
        df_fora_OP[['Status do Jogador', 'Jogador']] = df_fora_OP['Jogador'].str.split(' ', n=1, expand=True)
        colunas_fora = [col for col in df_fora_OP.columns if col != 'Status do Jogador'] + ['Status do Jogador']
        df_fora_OP = df_fora_OP[colunas_fora]

        # Acrescentando colunas no df_fora
        df_fora_OP['Time'] = nome_time_fora
        df_fora_OP['Adversário'] = nome_time_casa
        df_fora_OP['Rodada'] = rodada

        # Aplicando função de limpeza dos nomes dos times no df_fora
        df_fora_OP['Time'] = df_fora_OP['Time'].apply(limpar_nome_time)
        df_fora_OP['Adversário'] = df_fora_OP['Adversário'].apply(limpar_nome_time)

        # Juntando os data frames df_casa_OP e df_fora_OP e transformando em uma lista
        df_final_OP = pd.concat([df_casa_OP, df_fora_OP], ignore_index=True)
        df_total_OP.append(df_final_OP)

        # Aba Match Details:

        # Mudança para aba Match Details
        clicar_por_texto(navegador, wait, "MATCH DETAILS", "Aba Match Details")
        time.sleep(2)

        # Encontra o elemento do botão para selecionar o time de casa na aba Match Detais
        clicar_por_texto(navegador, wait, nome_time_casa, "Match Details - Casa")

        # Extração de dados html do time casa
        html_casa_MD = pegar_html_tabela_ativa(navegador, wait, "Match Details - Casa", 18)

        # Encontra o elemento do botão para selecionar o time de fora na aba Match Details
        clicar_por_texto(navegador, wait, nome_time_fora, "Match Details - Fora")

        # Extração de dados html do time fora
        html_fora_MD = pegar_html_tabela_ativa(navegador, wait, "Match Details - Fora", 18)

        # Parsear o contéudo html_casa_MD com o Beautiful Soup
        soup_casa_MD = BeautifulSoup(html_casa_MD, 'html.parser')
        tabela_casa_MD = soup_casa_MD.find(name='table')

        # Parsear o contéudo html_fora_MD com o Beautiful Soup
        soup_fora_MD = BeautifulSoup(html_fora_MD, 'html.parser')
        tabela_fora_MD = soup_fora_MD.find(name='table')

        # Estruturar conteúdos em data frame_casa - Pandas
        df_casa_MD = pd.read_html(StringIO(str(tabela_casa_MD)))[0]  # Faz a leitura do html parseado e estrutura num dataframe
        df_casa_MD = df_casa_MD.iloc[:-1]  # Retira a linha com o total

        print("\n[DEBUG] Colunas Match Details Casa:")
        print(list(df_casa_MD.columns))
        print("Quantidade de colunas:", len(df_casa_MD.columns))

        df_casa_MD.columns = ['Jogador', 'Posição', 'Passes Precisos', 'Chutes Na Trave', 'Chutes Dentro da Área',
                              'Chutes Fora da Área', 'Finalização de Cabeça', 'xG (Gols Esperados)', 'Tiros de Meta',
                              'Lateral', 'Gols Fora da Área', 'Gols de Perna Direita', 'Gols de Perna Esquerda',
                              'Gols de Cabeça', 'Gols de Penâlti', 'Gols de Falta', 'Fantasy Assist','Chances Criadas']  # Renomeia as colunas

        # Corrigir a coluna xG dividindo os valores por 1000
        df_casa_MD['xG (Gols Esperados)'] = df_casa_MD['xG (Gols Esperados)'].apply(lambda x: x / 1000 if x != 0 else 0)

        # Separando a informação da coluna Jogador em Status e Jogador, e descartando a coluna Status
        jogador_original = df_casa_MD['Jogador'].astype(str).str.strip()

        extracao = jogador_original.str.extract(r'^(Titular|Reservas)\s*(.*)$', expand=True)

        df_casa_MD['Jogador'] = extracao[1].where(
            extracao[1].notna() & (extracao[1].str.strip() != ''),
            jogador_original
        ).str.strip()

        # Acrescentando colunas
        df_casa_MD['Time'] = nome_time_casa
        df_casa_MD['Adversário'] = nome_time_fora
        df_casa_MD['Rodada'] = rodada

        # Aplicando função de limpeza dos nomes dos times no df_casa
        df_casa_MD['Time'] = df_casa_MD['Time'].apply(limpar_nome_time)
        df_casa_MD['Adversário'] = df_casa_MD['Adversário'].apply(limpar_nome_time)

        # Estruturar conteúdo em data frame_fora - Pandas
        df_fora_MD = pd.read_html(StringIO(str(tabela_fora_MD)))[0]  # Faz a leitura do html parseado e estrutura num dataframe
        df_fora_MD = df_fora_MD.iloc[:-1]  # Retira a linha com o total

        print("\n[DEBUG] Colunas Match Details Fora:")
        print(list(df_fora_MD.columns))
        print("Quantidade de colunas:", len(df_fora_MD.columns))

        df_fora_MD.columns = ['Jogador', 'Posição', 'Passes Precisos', 'Chutes Na Trave', 'Chutes Dentro da Área',
                              'Chutes Fora da Área', 'Finalização de Cabeça', 'xG (Gols Esperados)', 'Tiros de Meta',
                              'Lateral', 'Gols Fora da Área', 'Gols de Perna Direita', 'Gols de Perna Esquerda',
                              'Gols de Cabeça', 'Gols de Penâlti', 'Gols de Falta','Fantasy Assist','Chances Criadas']  # Renomeia as colunas

        # Corrigir a coluna xG dividindo os valores por 1000
        df_fora_MD['xG (Gols Esperados)'] = df_fora_MD['xG (Gols Esperados)'].apply(lambda x: x / 1000 if x != 0 else 0)

        # Separando a informação da coluna Jogador em Status e Jogador, e descartando a coluna Status
        jogador_original = df_fora_MD['Jogador'].astype(str).str.strip()

        extracao = jogador_original.str.extract(r'^(Titular|Reservas)\s*(.*)$', expand=True)

        df_fora_MD['Jogador'] = extracao[1].where(
            extracao[1].notna() & (extracao[1].str.strip() != ''),
            jogador_original
        ).str.strip()

        # Acrescentando colunas no df_fora
        df_fora_MD['Time'] = nome_time_fora
        df_fora_MD['Adversário'] = nome_time_casa
        df_fora_MD['Rodada'] = rodada

        # Aplicando função de limpeza dos nomes dos times no df_fora
        df_fora_MD['Time'] = df_fora_MD['Time'].apply(limpar_nome_time)
        df_fora_MD['Adversário'] = df_fora_MD['Adversário'].apply(limpar_nome_time)

        # Juntando os data frames df_casa_MD e df_fora_MD e transformando em uma lista
        df_final_MD = pd.concat([df_casa_MD, df_fora_MD], ignore_index=True)
        df_total_MD.append(df_final_MD)

    # Concatena os dataframes da lista em um só
    df_export_MS = pd.concat(df_total_MS, ignore_index=True)
    df_export_OP = pd.concat(df_total_OP, ignore_index=True)
    df_export_MD = pd.concat(df_total_MD, ignore_index=True)

    navegador.quit()

    # Caminho dos arquivos da base

    pasta_base = r"C:\CAMINHO_DA_PASTA"
    os.makedirs(pasta_base, exist_ok=True)

    arquivo_base_MS = os.path.join(pasta_base, "Copa do Mundo 2026 - Dados Principais.xlsx")
    arquivo_base_MD = os.path.join(pasta_base, "Copa do Mundo 2026 - Dados Alternativos.xlsx")
    arquivo_base_OP = os.path.join(pasta_base, "Copa do Mundo 2026 - Dados Alternativos_2.xlsx")

   # Função para agregar os dados sem sobrescrever

    def append_to_excel(novo_df, caminho_arquivo):
        try:
            pasta = os.path.dirname(caminho_arquivo)
            os.makedirs(pasta, exist_ok=True)

            if os.path.exists(caminho_arquivo):
                base_existente = pd.read_excel(caminho_arquivo)
                df_final = pd.concat([base_existente, novo_df], ignore_index=True)
            else:
                df_final = novo_df

            df_final.to_excel(caminho_arquivo, index=False)
            print(f"[OK] Arquivo salvo em: {caminho_arquivo}")

        except PermissionError:
            messagebox.showerror(
                "Erro ao salvar",
                f"Não consegui salvar o arquivo:\n\n{caminho_arquivo}\n\n"
                "Provavelmente ele está aberto no Excel ou sem permissão de escrita.\n"
                "Feche o arquivo e rode novamente."
            )
            raise

    # Concatena com a base
    append_to_excel(df_export_MS, arquivo_base_MS)
    append_to_excel(df_export_MD, arquivo_base_MD)
    append_to_excel(df_export_OP, arquivo_base_OP)

    # Caixa de Mensagem informando a finalização da extração
    messagebox.showinfo("Sucesso", "A extração de dados foi concluída!")

# Criação da Janela Gráfica

ctk.set_appearance_mode('dark')
janela = ctk.CTk()
janela.geometry('540x700')
janela.title("Webscraping de Dados - FIFA World Cup 2026")

# Texto de Label para inserir a quantidade de jogos
texto_quant_jogos = ctk.CTkLabel(janela, text="Insira a quantidade de jogos que você deseja extrair os dados:")
texto_quant_jogos.grid(row=0,column=0, padx=10,pady=10, sticky='w')

# Texto para orientação do preenchimento da quantidade de jogos
# texto_quant_jogos2 = ctk.CTkLabel(janela, text="(A quantidade deve ser contada do jogo mais recente para o último.)",font=("Arial",11))
# texto_quant_jogos2.grid(row=1,column=0, padx=10,sticky="w")

# Campo de entrada para a quantidade de jogos
entrada_jogos = ctk.CTkEntry(janela)
entrada_jogos.grid(row=0,column=1, padx=10, pady=10)

# Texto para inserir o número da rodada
texto_rodada = ctk.CTkLabel(janela, text="Insira o número da rodada referente aos jogos:")
texto_rodada.grid(row=3,column=0, padx=10, pady=10, sticky='w')

# Campo de entrada para o número da rodada
entrada_rodada = ctk.CTkEntry(janela)
entrada_rodada.grid(row=3,column=1, padx=10, pady=10)

# Botão para acionar o comando de buscar os links
botao_pegar_links =ctk.CTkButton(janela, text="Buscar Links", command=buscar_links_jogos)
botao_pegar_links.grid(row=5,column=1, pady=20)

# Texto de resultado com os links e os jogos
resultado_textbox =ctk.CTkTextbox(janela, width=500, height=350, border_width=2, border_color="gray")
resultado_textbox.grid(row=7, column=0, columnspan=2, sticky="w", padx=20, pady=10)

# Botão para limpar os campos
botao_limpar_campos =ctk.CTkButton(janela, text="Limpar Campos", command=limpar_campos)
botao_limpar_campos.grid(row=8,column=0,padx=20,pady=10, sticky="w")

# Botão para fazer a extração dos dados
botao_extrair_dados =ctk.CTkButton(janela, text="Extrair Dados", command=extrair_dados, state="disabled")
botao_extrair_dados.grid(row=8,column=1,pady=10)

# Texto informando a extração de dados


janela.mainloop()
