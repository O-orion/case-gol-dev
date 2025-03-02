# GOL Flight Stats

![GOL Flight Stats](https://via.placeholder.com/800x200.png?text=GOL+Flight+Stats)  
*Análise de dados estatísticos de voos da GOL com Flask e Docker*

Bem-vindo ao **GOL Flight Stats**, uma aplicação web desenvolvida para o case de desenvolvedor da GOL. Este projeto processa dados públicos da ANAC, exibe estatísticas de voos da GOL (RPK por mercado e período) e oferece autenticação de usuários, tudo empacotado em um contêiner Docker.

---

## Visão Geral

Essa aplicação:
- Filtra dados de voos regulares domésticos da GOL (EMPRESA_SIGLA = "GLO", GRUPO_DE_VOO = "REGULAR", NATUREZA = "DOMÉSTICA").
- Cria a coluna `MERCADO` agrupando aeroportos de origem e destino em ordem alfabética (ex.: `SBGRSBSV`).
- Gera gráficos interativos de RPK por mercado e intervalo de datas.
- Inclui autenticação segura com login e registro de usuários.

### Tecnologias Utilizadas
- **Backend**: Flask, Flask-SQLAlchemy, SQLAlchemy, Pandas, Pydantic
- **Frontend**: Bootstrap 5, Chart.js
- **Banco de Dados**: SQLite
- **Contêiner**: Docker com Gunicorn
- **Deploy**: Render

---

## Como Executar Localmente

### Pré-requisitos
- Python 
- Git
- Docker

### Instalação
1. Clone o repositório:
   ```bash
   git clone https://github.com/O-orion/case-gol-dev
   cd case-gol-dev

2. Crie e ative um ambiente virtual:
    1 - python -m venv venv
    2 - source venv/bin/activate  # Linux/Mac
    3 - venv\Scripts\activate     # Windows

3. Instale as dependências:
    pip install -r requirements.txt

4. Processe os dados da ANAC pra criar o banco
    1 - Crie a pasta data e dentro dela coloque o arquivo CSV
    2 - Altere o caminho para o arquivo csv que está dentro do arquivo data_processing.py
    3 - rode o seguinte comando: python app/data_processing.py

5. Inicie a aplicação
    1 -  Abra o prompt de comando
    2 -  Navegue até a pasta raiz do projeto
    3 -  Execute o seguinte comando: python run.py

## Como Executar com Docker
### Pré-requisitos
 - Docker instalado

### Instruções
 1 - Baixe a imagem do Docker Hub: docker pull oorionn/gol-flight-stats:latest
 2 - Rode o contêiner: docker run -p 5000:8000 seu-usuario/gol-flight-stats:latest

## Deploy Online
A aplicação está disponível online para teste: https://gol-flight-stats.onrender.com


## Funcionalidades
    Autenticação: Registro e login de usuários com validação.
    Filtros: Selecione mercados (ex.: SBGRSBSV) e intervalos de datas (ano/mês).
    Gráficos: Visualização de RPK em linha ou barra, dependendo do número de pontos.
    Responsividade: Interface adaptável com Bootstrap.

---

### **Personalização**

1. **Oorionn**
2. **[URL do Render](https://gol-flight-stats.onrender.com)**
3. **Lucas Viana / O-orion**
