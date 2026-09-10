# ⚽ Copa do Mundo 2026 — Projeto de Business Intelligence & Data Analytics

Projeto completo de Business Intelligence desenvolvido a partir de dados da Copa do Mundo 2026, cobrindo todo o pipeline de dados: **extração automatizada (web scraping), tratamento/ETL, modelagem relacional, DAX e criação de dashboards interativos.**

* **Artigo Completo:** [Clique aqui para ler a análise detalhada no LinkedIn](https://www.linkedin.com/pulse/o-que-aprendi-construindo-um-projeto-completo-de-business-preuss-dgdhf/?trackingId=a6AdigIGTKmA5OV%2FUfgcig%3D%3D)

---

## 📸 Dashboards e Visualizações


![Seleções - Tabela Geral](imagens/Seleções%20-%20Tabela%20Geral.png)

<br>

![Seleções - Detalhamento Finalizações](imagens/Seleções%20-%20Detalhamento%20Finalizações.png)

<br>

![Jogadores - Participação](imagens/Jogadores%20-%20Participação.png)

<br>

![Jogadores - Atributos dos Goleiros](imagens/Jogadores%20-%20Atributos%20dos%20Goleiros.png)

<br>

![Jogadores - Atributos de Defesa](imagens/Jogadores%20-%20Atributos%20de%20Defesa.png)

<br>

![Jogadores - Atributos de Ataque](imagens/Jogadores%20-%20Atributos%20de%20Ataque.png)

<br>

![Análise Exploratória - Seleções - Defesa - Ações Defensivas x Gols Sofridos](imagens/Análise%20Exploratória%20-%20Seleções%20-%20Defesa%20-%20Ações%20Defensivas%20x%20Gols%20Sofridos.png)

<br>

![Análise Exploratória - Seleções - Defesa - Ações Defensivas x Disciplina](imagens/Análise%20Exploratória%20-%20Seleções%20-%20Defesa%20-%20Ações%20Defensivas%20x%20Disciplina.png)

<br>

![Análise Exploratória - Seleções - Ataque e Defesa - xG Sofrido x xG Feito](imagens/Análise%20Exploratória%20-%20Seleções%20-%20Ataque%20e%20Defesa%20-%20xG%20Sofrido%20x%20xG%20Feito.png)

<br>

![Análise Exploratória - Jogadores - Defesa - Ações Defensivas x Disciplina](imagens/Análise%20Exploratória%20-%20Jogadores%20-%20Defesa%20-%20Ações%20Defensivas%20x%20Disciplina.png)

<br>

![Análise Exploratória - Jogadores - Ataque - xG x Gols Marcados](imagens/Análise%20Exploratória%20-%20Jogadores%20-%20Ataque%20-%20xG%20x%20Gols%20Marcados.png)

<br>
<br>

---

## 🛠️ Tecnologias e Ferramentas Utilizadas

* **Linguagem & Automação:** Python (Selenium, BeautifulSoup, Pandas)
* **Armazenamento / Bases:** Microsoft Excel
* **ETL & Modelagem:** Power Query
* **Visualização & Analytics:** Power BI & DAX

---

## 📂 Estrutura do Repositório

* 🖼️ **`imagens`** — Imagens e capturas de tela dos dashboards
* 📄 **`python/extracao_dados.py`** — Script automatizado de web scraping com interface gráfica
* 📝 **`README.md`** — Documentação e instruções do projeto

  
---

## ⚙️ Como Executar o Script de Extração (`extracao_dados.py`)

Para reproduzir a extração dos dados localmente na sua máquina, siga os passos:

### 1. Pré-requisitos
Crie uma pasta no seu computador para servir como diretório base do projeto. Dentro dela, crie **três arquivos Excel vazios** exatamente com os seguintes nomes:

* `Copa do Mundo 2026 - Dados Principais.xlsx`
* `Copa do Mundo 2026 - Dados Alternativos.xlsx`
* `Copa do Mundo 2026 - Dados Alternativos_2.xlsx`

### 2. Configuração do Script
1. Abra o arquivo `extracao_dados.py`.
2. Localize a variável `pasta_base` (linha 715 no script) e altere apenas o caminho para o diretório criado no **Passo 1**:

`pasta_base = r"C:\CAMINHO_DA_SUA_PASTA"`

> **Nota:** Não é necessário alterar o nome dos 3 arquivos no código; o script irá localizá-los e preenchê-los automaticamente.

### 3. Execução e Interação com a Interface Gráfica
1. Execute o script `extracao_dados.py` no seu ambiente Python (clicando em **Run / Play** na sua IDE de preferência, como PyCharm ou VS Code).
2. Uma **janela gráfica (interface Tkinter)** será exibida solicitando os parâmetros da extração:
   * **Quantidade de Jogos:** Informe o número de partidas que deseja analisar. A lista de jogos é ordenada cronologicamente (do mais recente para o mais antigo). O script fará a leitura de cima para baixo (ex: se digitar `10`, ele extrairá os 10 jogos mais recentes).
   * **Número da Rodada:** Insira a rodada correspondente aos dados que estão sendo extraídos.

> **Nota sobre o campo "Rodada":** O script atribui a rodada informada na janela a todos os jogos processados naquela execução batch. Caso execute a raspagem de múltiplos jogos de rodadas distintas em uma única etapa, este campo registrará o valor digitado para todos os registros no Excel, sendo necessária a edição pontual da coluna diretamente na planilha, se desejado.

---

## 📌 Fonte dos Dados e Observações
* Os dados são provenientes de fontes públicas sobre futebol e estatísticas da Copa do Mundo.
* O script foi construído especificamente para raspagem, padronização e estruturação automatizada dessas bases.

---

## ✉️ Contato

* **Perfil / Contato:** [Conecte-se comigo no LinkedIn](https://www.linkedin.com/in/thiago-preuss-543aba78/)
