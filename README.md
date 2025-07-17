# Analisador de Contratos com IA

API RESTful que utiliza Inteligência Artificial para extrair e organizar informações-chave de contratos nos formatos PDF e DOCX. O objetivo é agilizar a análise documental, tornando o processo mais eficiente para profissionais que lidam com grandes volumes de contratos.

## ⚙️ Tecnologias Utilizadas

- [Langchain](https://www.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLModel](https://sqlmodel.tiangolo.com/)
- [PyPDF2](https://pypi.org/project/PyPDF2/)

## 📑 Tópicos

1. Construção  
2. Funcionalidades  
3. Frontend  
4. Site Hospedado  
5. Como usar na sua máquina  

---

## 1 - Construção 🏗️

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




