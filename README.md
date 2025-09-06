# Soccer Analytics

Dashboard web desenvolvido para analisar e prever resultados de partidas de futebol com base em dados estatísticos. A aplicação utiliza a API [football-data.org](https://www.football-data.org) para obter informações em tempo real sobre classificações, confrontos diretos, desempenho recente das equipes e artilharia do campeonato.

A interface criada com HTML, CSS e JavaScript permite que o usuário insira o nome de duas equipes e receba uma análise comparativa detalhada, incluindo probabilidades de vitória, empate e derrota.

<img width="815" height="617" alt="image" src="https://github.com/user-attachments/assets/5f4143eb-1f14-404a-b819-84755ca892e4" />


## 📋 Funcionalidades

* **Previsão de Resultados:** Calcula as probabilidades de vitória para cada time e a chance de empate, com base em um algoritmo ponderado.
* **Análise Comparativa:** Exibe estatísticas lado a lado para:
    * **Confronto Direto (H2H):** Histórico de vitórias e gols marcados nos últimos 5 jogos entre as equipes.
    * **Fase Atual:** Desempenho recente (vitórias e gols) nos últimos 5 jogos de cada time.
* **Informações da Tabela:** Mostra a posição atual de cada equipe no campeonato.
* **Artilheiros:** Lista os principais goleadores da competição.
* **Interface Dinâmica:** Gráficos e logos das equipes são atualizados dinamicamente a cada nova análise.

## ⚙️ Como Funciona o Algoritmo de Previsão

A probabilidade de vitória é calculada através de um "Power Score" para cada time, que leva em consideração três fatores principais com pesos diferentes:

1.  **Confronto Direto (Peso: 40%):** A taxa de vitória histórica no confronto direto entre as duas equipes.
2.  **Fase Atual (Peso: 35%):** A taxa de vitória nos últimos 5 jogos disputados no campeonato.
3.  **Posição na Tabela (Peso: 25%):** A classificação atual de cada time na competição.

A fórmula para o Power Score de um time é:
$$\text{Power Score} = (\text{Fator H2H} \times 0.40) + (\text{Fator Fase} \times 0.35) + (\text{Fator Tabela} \times 0.25)$$

As probabilidades finais são normalizadas e ajustadas pela probabilidade histórica de empates entre as equipes.

## 🛠️ Tecnologias Utilizadas

* **Backend:**
    * **Python 3:** Linguagem principal para a lógica do servidor.
    * **Flask:** Micro-framework web para criar a API e servir a aplicação.
    * **Requests:** Biblioteca para realizar as chamadas à API `football-data.org`.
* **Frontend:**
    * **HTML5:** Estrutura da página.
    * **CSS3:** Estilização da interface, com design responsivo e moderno.
    * **JavaScript (Vanilla):** Manipulação dinâmica do DOM e comunicação com o backend via `fetch` API.
* **API Externa:**
    * [football-data.org API](https://www.football-data.org): Fonte de todos os dados estatísticos de futebol.

## 🚀 Instalação e Execução

Para executar este projeto localmente, siga os passos abaixo.

### Pré-requisitos

* **Python 3.6** ou superior.
* **PIP** (gerenciador de pacotes do Python).
* Uma **chave de API** gratuita do site [football-data.org](https://www.football-data.org/client/register).

### Passos

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/seu-usuario/seu-repositorio.git](https://github.com/seu-usuario/seu-repositorio.git)
    cd seu-repositorio
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate

3.  **Instale as dependências:**
    O projeto depende das bibliotecas `Flask` e `requests`. Instale-as com o seguinte comando:
    ```bash
    pip install Flask requests
    ```

4.  **Configure a Chave da API:**
    Abra o arquivo `app.py` em um editor de texto e substitua o valor da variável `API_KEY` pela sua chave obtida no site `football-data.org`.

    ```python
    API_KEY = "SUA_CHAVE_DE_API_AQUI"
    ```

5.  **Execute a aplicação:**
    Com o ambiente virtual ativado e as dependências instaladas, inicie o servidor Flask:
    ```bash
    python app.py
    ```

6.  **Acesse no navegador:**
    Abra seu navegador e acesse o seguinte endereço:
    [http://127.0.0.1:5000](http://127.0.0.1:5000)

## 🔧 Configuração e Personalização

Dentro do arquivo `app.py`, você pode personalizar algumas variáveis de configuração:

* `COMPETITION_CODE`: Altere o código da competição para analisar outros campeonatos (ex: 'PL' para a Premier League, 'CL' para a Champions League). O padrão é `'BSA'` (Campeonato Brasileiro Série A).
* `PESO_H2H`, `PESO_FASE`, `PESO_TABELA`: Modifique os pesos para ajustar a importância de cada fator no cálculo do "Power Score". A soma dos pesos não precisa ser obrigatoriamente 1.
