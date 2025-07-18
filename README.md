# Analisador de Contratos com IA

API RESTful que utiliza Inteligência Artificial para extrair e organizar informações-chave de contratos nos formatos PDF e DOCX. O objetivo é agilizar a análise documental, tornando o processo mais eficiente para profissionais que lidam com grandes volumes de contratos.

## ⚙️ Tecnologias Utilizadas

- [Langchain](https://www.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)

## 📑 Tópicos

- [1 - Estrutura](#1---estrutura-)
- [2 - Funcionalidades da API](#2---funcionalidades-da-api-)
- [3 - Frontend](#3---frontend-)
- [4 - Site Hospedado](#4---site-hospedado-)
- [5 - Como usar na sua máquina (Obsoleto)](#5---como-usar-na-sua-máquina-obsoleto-)
- [6 - Como usar na sua máquina (ATUALIZADO)](#6---como-usar-na-sua-máquina-atualizado-)
---

## 1 - Estrutura 🏗️

A aplicação foi desenvolvida em **Python 3.13.15**, com suporte a dois bancos de dados relacionais: **MySQL** e **PostgreSQL** (hospedado via Render).

A estrutura foi organizada em módulos, promovendo legibilidade, escalabilidade e facilidade de manutenção.

### 📁 Estrutura de Diretórios

```text
📂 app/
├── 📁 __pycache__/
├── 📄 __init__.py
├── 📄 auth.py
├── 📄 crud.py
├── 📄 database.py
├── 📄 main.py
├── 📄 models.py
├── 📄 processing.py
├── 📄 schemas.py
└── 📄 utils.py
📂 front/
├── 📄 index.html
├── 📄 script.js
└── 📄 style.css
📂 tests/
├── 📁 __pycache__/
├── 📄 __init__.py
├── 📄 conftest.py
└── 📄 test_api.py
```

### 📦 Organização dos Módulos

A pasta `app/` é responsável por toda a lógica da aplicação e contém os seguintes arquivos:

- `auth.py`: gerencia a autenticação de usuários.
- `crud.py`: implementa operações de Create, Read, Update e Delete no banco de dados.
- `database.py`: configuração e inicialização do banco de dados.
- `main.py`: define os endpoints e lógica principal da API.
- `models.py`: contém os modelos das tabelas do banco (`User`, `Contract`).
- `processing.py`: integração com a IA (Gemini 2.5-flash) para extração dos dados via prompt.
- `schemas.py`: define os esquemas de entrada e saída da API com Pydantic.
- `utils.py`: funções auxiliares para leitura e manipulação de arquivos `.pdf` e `.docx`.

A pasta `front/` contém a interface web, composta por:

- `index.html`: estrutura básica da interface.
- `script.js`: lógica de integração com a API via JavaScript.
- `style.css`: estilização da interface.

### 🧪 Testes

Com o auxílio da biblioteca **PyTest**, foram desenvolvidos testes automatizados localizados na pasta `tests/`. Esses testes cobrem os principais fluxos da aplicação, incluindo rotas públicas, autenticação, upload e acesso a endpoints protegidos.

Abaixo estão os cenários testados:

#### ✅ Rotas públicas

- `GET /`  
- `POST /users/`  
  Payload de exemplo:
  ```json
  {
    "username": "testuser",
    "password": "testpassword"
  }
  ```

#### 🔐 Fluxo de autenticação

- `POST /users/`  
  ```json
  {
    "username": "logintest",
    "password": "password123"
  }
  ```
- `POST /login`  
  Enviado como dados de formulário:
  ```text
  username=authuser&password=password123
  ```

#### 🔒 Acesso a rotas protegidas

- `GET /contracts/list/filenames`  
- `POST /login` com autenticação e geração de token JWT

#### 📤 Teste de upload com IA simulada

Foi utilizada uma função mock que simula a resposta da IA, interceptando a chamada real ao modelo e retornando dados fictícios. Isso permite testar o comportamento da API sem depender da comunicação direta com a IA, garantindo agilidade e isolamento nos testes.

---

Esses testes aumentam a confiabilidade da aplicação e ajudam a prevenir regressões, garantindo que os principais fluxos funcionem corretamente antes de cada deploy.

## 2 - Funcionalidades da API 🚀

A seguir estão listadas todas as rotas disponíveis com exemplos de requisição, parâmetros, tipos e respostas presentes em main.py.

---

### `GET /`

**Descrição**: Verifica se a API está online.

**Resposta (JSON)**:

```json
{ "status": "API is running!" }
```
---

### `POST /users/`

**Descrição**: Cria um novo usuário.

**Parâmetros (JSON Body, schemas.UserCreate)**:

```json
{
  "username": "joao",
  "password": "senha123"
}
```

**Resposta (models.UserRead)**:

```json
{
  "id": 1,
  "username": "joao"
}
```
---

### `POST /login`

**Descrição**: Realiza o login e retorna um token JWT.

**Parâmetros (form-data)**:
- username: Nome de usuário (string)
- password: Senha (string)

**Resposta (schemas.Token)**:

```json
{
  "access_token": "<jwt_token>",
  "token_type": "bearer"
}
```

---

### `GET /users/me`

**Descrição**: Retorna os dados do usuário autenticado.

**Cabeçalho**:
- Authorization: Bearer <token>

**Resposta (models.UserRead)**:

```json
{
  "id": 1,
  "username": "joao"
}
```

---

### `POST /contracts/upload`

**Descrição**: Envia um contrato para ser processado pela IA.

**Parâmetros**:
- Arquivo .pdf ou .docx (campo file, via multipart/form-data)

**Cabeçalho**:
- Authorization: Bearer <token>

**Resposta (models.Contract)**:

```json
{
  "id": 2,
  "filename": "contrato1.pdf",
  "status": "completed",
  "contracting_party": "Empresa A",
  "contracted_party": "Empresa B",
  "contract_value": "R$ 500.000",
  "main_obligations": "Entrega mensal de produtos",
  "additional_data": "Válido por 12 meses",
  "termination_clause": null
}
```

---

### `GET /contracts/{contract_name}`

**Descrição**: Busca os dados de um contrato pelo nome do arquivo.

**Parâmetros de rota**:
- contract_name (string): Exemplo: contrato1.pdf

**Cabeçalho**:
- Authorization: Bearer <token>

**Resposta (models.Contract)**:

```json
{
  "id": 2,
  "filename": "contrato1.pdf",
  "status": "completed",
  "contracting_party": "Empresa A",
  "contracted_party": "Empresa B",
  "contract_value": "R$ 500.000",
  "main_obligations": "Entrega mensal de produtos",
  "additional_data": "Dados adicionais aqui",
  "termination_clause": "Cláusula de rescisão"
}
```

---

### `GET /contracts/list/filenames`

**Descrição**: Lista todos os nomes dos contratos existentes.

**Cabeçalho**:
- Authorization: Bearer <token>

**Resposta (lista de strings)**:

```txt
[
  "contrato1.pdf",
  "contrato2.docx"
]
```
---

### `DELETE /contracts/{contract_id}`

**Descrição**: Exclui um contrato pelo ID.

**Parâmetro de rota**:
- contract_id (int): Exemplo: 2

**Cabeçalho**:
- Authorization: Bearer <token>

**Resposta (models.Contract)**:

```json
{
  "id": 2,
  "filename": "contrato1.pdf",
  "status": "completed",
  "contracting_party": "Empresa A",
  "contracted_party": "Empresa B",
  "contract_value": "R$ 500.000",
  "main_obligations": "Entrega mensal de produtos",
  "additional_data": "Dados adicionais aqui",
  "termination_clause": "Cláusula de rescisão"
}
```
---

## 3 - Frontend 🌐

### Tela inicial de Login - Usuário e Senha
![Tela Inicial](images_readme/tela1.png)

### Tela secundária com a implementação
![Tela Secundária](images_readme/tela2.png)

Não irei me aprofundar muito na implementação do frontend, mas basicamente a comunicação foi feita diretamente via JavaScript com a API, utilizando requisições assíncronas (`fetch`). O código manipula a interface exibindo ou ocultando seções conforme o usuário realiza login, upload, busca, listagem ou exclusão de contratos.

O fluxo geral funciona assim:

- **Login:** Envia os dados via `POST /login`, recebe o token JWT e, se o login for bem-sucedido, exibe a interface principal para o usuário.
- **Upload:** Permite enviar um arquivo PDF ou DOCX para a API (`POST /contracts/upload`), exibindo mensagens de status e resultados formatados.
- **Busca:** Consulta um contrato pelo nome do arquivo (`GET /contracts/{filename}`) e apresenta os dados retornados em formato JSON formatado.
- **Listagem:** Busca todos os nomes dos contratos existentes (`GET /contracts/list/filenames`) e os exibe numa lista na página.
- **Exclusão:** Permite deletar um contrato pelo nome; para isso, primeiro busca o contrato para obter seu ID e depois realiza a exclusão via `DELETE /contracts/{id}`, mostrando feedback visual e mensagens adequadas.

Além disso, o código controla o estado dos botões e indicadores de carregamento para garantir boa usabilidade e prevenir múltiplos envios simultâneos, além de tratar erros exibindo mensagens claras para o usuário.

Em resumo, a interface é leve e responsiva, fazendo chamadas REST para a API e atualizando dinamicamente o conteúdo da página com os dados retornados, sem necessidade de recarregar a página.

---

## 4 - Site Hospedado 💻

O site, a API e o banco de dados PostgreSQL estão completamente hospedados na plataforma [Render](https://render.com/), utilizando a versão gratuita do serviço. 

É importante destacar que, devido às limitações da camada gratuita, os serviços podem entrar em um estado de "hibernação" ou inatividade após períodos sem uso, o que pode causar um pequeno atraso no tempo de resposta inicial quando o sistema é acessado novamente. Além disso, o plano gratuito oferece recursos limitados de processamento e memória, o que pode impactar a performance em picos de uso ou operações mais pesadas (Principalmente da API).

#### Tela de exemplo de espera
![Tela Espera](images_readme/tela_espera.jpeg)

[👉 Acesse o site aqui](https://site-contratos-marcos.onrender.com/)
[👉 Acesse a API aqui](https://analisador-contratos.onrender.com/)

> ⚠️ **Observação:** Recomenda-se utilizar o banco de dados **MySQL** ao rodar a API ou o site localmente, pois sua configuração é mais simples nesse contexto.  
> 
> No entanto, para a versão hospedada, foi utilizado o **PostgreSQL** (via Render), mantendo a mesma estrutura e lógica de acesso ao banco de dados.  
>
> No próximo tópico, você aprenderá como rodar o projeto localmente com o banco configurado corretamente.


## 5 - Como usar na sua máquina (Obsoleto)❓

### ✅ Pré-requisitos

- **Python 3.13.15** (recomendado, versões 3.10+ também devem funcionar)
- **Editor de código** (Recomendo o [Visual Studio Code](https://code.visualstudio.com/))
- **Chave da API do Gemini**

---

### 🧭 Passo a passo

1. **Clone o repositório**
   
   Abra o terminal na pasta onde deseja salvar o projeto e execute:

   ```bash
   git clone https://github.com/Marocosz/Analisador_Contrato.git
   ``` 

   Ou, se preferir, baixe o `.zip` diretamente pelo GitHub:

   ![Zip Github](images_readme/zip_github.png)

---

2. **Crie o ambiente virtual**

   No terminal, dentro da pasta do projeto, execute:

   ```bash
   python -m venv venv
   ```

   Depois ative com:

   ```bash
   .\venv\Scripts\activate
   ```

   > Obs: Em alguns casos no PowerShell, você pode precisar executar diretamente o script `Activate.ps1` dentro da pasta `venv\Scripts`.

---

3. **Instale as dependências**

   Com o ambiente virtual ativado, instale as bibliotecas com:

   ```bash
   pip install -r requirements.txt
   ```

   > O arquivo `requirements.txt` já está no repositório e contém apenas as bibliotecas essenciais para o projeto.

---

4. **Configuração do ambiente**

   Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

   ```env
   GEMINI_API_KEY="sua_key_api"
   JWT_KEY="sua_encryption_key"
   ```

   - A variável `GEMINI_API_KEY` deve conter sua chave da API do Gemini.
   - Para `JWT_KEY`, recomendo usar uma chave com 256 bits (32 caracteres aleatórios) para segurança do sistema de autenticação JWT.

---

5. **Adaptação para ambiente local**

   #### a) Arquivo `database.py`  
   Localize e edite as seguintes linhas:

   ```python
   # Linha 5 - Comente a opção online:
   # DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")  # Online

   # Linha 6 - Descomente a opção local:
   DATABASE_URL = "sqlite:///database.db"  # Local
   ```

   #### b) Arquivo `script.js`  
   Atualize a URL da API:

   ```js
   // De:
   const API_URL = 'https://analisador-contratos.onrender.com';

   // Para:
   const API_URL = 'http://127.0.0.1:8000';
   ```

---

### 🚀 Pronto!

Com tudo configurado, você já pode rodar a aplicação localmente.

#### 1️⃣ Iniciar a API

Com o ambiente virtual (`venv`) ativado, execute o seguinte comando para iniciar a API FastAPI:

```bash
uvicorn main:app --reload
```

A API estará acessível em: [http://127.0.0.1:8000](http://127.0.0.1:8000)

Você também pode visualizar a documentação interativa da API em:
- [Swagger UI](http://127.0.0.1:8000/docs)
- [Redoc](http://127.0.0.1:8000/redoc)

---

#### 2️⃣ Iniciar o site (frontend)

Abra **um novo terminal** (com a `venv` ativada), navegue até a pasta do projeto e execute:

```bash
python -m http.server 8080
```

O servidor local estará disponível em:

[http://localhost:8080](http://localhost:8080)

Nele, localize e entre na pasta `front` para acessar o site.


### Criando seu usuário

Para criar seu usuário, acesse a documentação da API no Swagger UI:

- Local: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- Online: [https://analisador-contratos.onrender.com/docs](https://analisador-contratos.onrender.com/docs)

---

### Passo a passo para criar e autenticar um usuário

#### 1️⃣ Criar um usuário

- Navegue até o endpoint **POST /users/**.  
- Clique em **"Try it out"**.  
- No corpo da requisição, informe o username e password, por exemplo:

    {
      "username": "marco",
      "password": "123"
    }

- Clique em **"Execute"**.  
- Se tudo ocorrer bem, você verá a resposta indicando que o usuário foi criado com sucesso.

---

#### 2️⃣ Fazer login

- Navegue até o endpoint **POST /login**.  
- Clique em **"Try it out"**.  
- No corpo da requisição, informe o mesmo username e password usados na criação, exemplo:

    {
      "username": "marco",
      "password": "123"
    }

- Clique em **"Execute"**.  

---

#### 3️⃣ Acessar endpoints protegidos

- Navegue até o endpoint **GET /users/me**.  
- No canto superior direito da página do Swagger, clique em **"Authorize"** (um cadeado).  
- Coloque as credenciais (username e password) que você criou anteriormente.
- Clique em **"Authorize"** e depois feche a janela.  
- Agora, no endpoint **GET /users/me**, clique em **"Try it out"** e depois em **"Execute"** para testar o acesso autenticado.

---

Pronto! Você criou seu usuário, autenticou e acessou um endpoint protegido usando o token JWT via Swagger UI.

---

## 6 - Como usar na sua máquina (ATUALIZADO) 🐳

Este projeto foi atualizado para virar totalmente containerizado com Docker, o que torna a configuração do ambiente de desenvolvimento incrivelmente simples e rápida.

### ✅ Pré-requisitos

- **Docker Desktop**: É a **única ferramenta obrigatória**. Garante que você tenha o Docker e o Docker Compose. Baixe no [site oficial](https://www.docker.com/products/docker-desktop/).
- **Git**: Para clonar o repositório.
- **Chave da API do Gemini**: Para a funcionalidade de análise com IA.

---

### 🧭 Passo a passo

1. **Clone o repositório**
   
   Abra o terminal na pasta onde deseja salvar o projeto e execute:

   ```bash
   git clone https://github.com/Marocosz/Analisador_Contrato.git
   ``` 

   Ou, se preferir, baixe o `.zip` diretamente pelo GitHub:

   ![Zip Github](images_readme/zip_github.png)

---

2. **Crie e configure o Arquivo de Ambiente (.env)**

    As senhas e chaves secretas não ficam no código. Você precisa criá-las em um arquivo local para o Docker poder usá-las

    - Na raiz do projeto, crie um arquivo chamado `.env`

    - Copie e cole o seguinte conteúdo dentro dele, substituindo pelos seus próprios valores:
    
      ```text
      # Pode usar o banco de dados que tenho hospedado no render!!
      DATABASE_URL="postgresql://contratos_db_ug75_user:7Nh2fAWfDPtgZJiXiwHZ1VYmbYUNDRy3@dpg-d1s5vp95pdvs73a3tmhg-a.virginia-postgres.render.com/contratos_db_ug75"

      # Sua chave de API do Google Gemini
      GEMINI_API_KEY="sua-chave-aqui"

      # Uma chave secreta aleatória para a autenticação (ex: JWT_KEY, etc.)
      JWT_KEY="uma-chave(recomendo usar uma chave com 256 bits (32 caracteres aleatórios) para segurança do sistema de autenticação JWT.)"
      ```

---

3. **Suba a aplicação!**
  
    Com o docker Desktop rodando no seu computador, execute o seguinte comando no terminal, na raiz do projeto:
    
      ```bash
      docker compose up --build
      ```
  
---

4. **Acesse a Aplicação**

    Seu ambiente completo está no ar!

    OBS: Você pode usar um usuário que já criei

         Usuário: marcos

         Senha: 123

    - Acesse o frontend por: [http://localhost:8080](http://localhost:8080)
    - Acesse a doc da api por: [http://localhost:8000/docs](http://localhost:8000/docs)

### Passo a passo para criar e autenticar um usuário

Dentro da documentação da api:

#### 1️⃣ Criar um usuário

- Navegue até o endpoint **POST /users/**.  
- Clique em **"Try it out"**.  
- No corpo da requisição, informe o username e password, por exemplo:

    {
      "username": "marcos",
      "password": "123"
    }

- Clique em **"Execute"**.  
- Se tudo ocorrer bem, você verá a resposta indicando que o usuário foi criado com sucesso.

---

#### 2️⃣ Fazer login

- Navegue até o endpoint **POST /login**.  
- Clique em **"Try it out"**.  
- No corpo da requisição, informe o mesmo username e password usados na criação, exemplo:

    {
      "username": "marco",
      "password": "123"
    }

- Clique em **"Execute"**.  

---

#### 3️⃣ Acessar endpoints protegidos

- Navegue até o endpoint **GET /users/me**.  
- No canto superior direito da página do Swagger, clique em **"Authorize"** (um cadeado).  
- Coloque as credenciais (username e password) que você criou anteriormente.
- Clique em **"Authorize"** e depois feche a janela.  
- Agora, no endpoint **GET /users/me**, clique em **"Try it out"** e depois em **"Execute"** para testar o acesso autenticado.

---

Pronto! Você criou seu usuário, autenticou e acessou um endpoint protegido usando o token JWT via Swagger UI.

---

### 🛠 Suporte

Se tiver dúvidas, sugestões ou encontrar algum erro, sinta-se à vontade para abrir uma _issue_ no repositório:

👉 [https://github.com/Marocosz/Analisador_Contrato](https://github.com/Marocosz/Analisador_Contrato)