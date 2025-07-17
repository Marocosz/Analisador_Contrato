document.addEventListener('DOMContentLoaded', () => {
    // Selecionando os elementos da página
    const loginSection = document.getElementById('login-section');
    const appSection = document.getElementById('app-section');
    const uploadForm = document.getElementById('upload-form');
    const loginForm = document.getElementById('login-form');
    const searchForm = document.getElementById('search-form');
    const resultSection = document.getElementById('result-section');
    const loadingDiv = document.getElementById('loading');
    const listFilesButton = document.getElementById('list-files-button');
    const contractsListOutput = document.getElementById('contracts-list-output');
    const deleteContractForm = document.getElementById('delete-contract-form');
    const deleteFilenameInput = document.getElementById('delete-filename');

    // http://127.0.0.1:8000 para local
    // https://analisador-contratos.onrender.com render
    const API_URL = 'https://analisador-contratos.onrender.com';    // ATUALIZAAAAA
    let apiToken = null;

    // Função para formatar a saída de Upload e Busca
    function displayResult(data) {
        contractsListOutput.innerHTML = ''; // Limpa a lista de contratos, se houver
        let formattedJson = JSON.stringify(data, null, 2);
        resultSection.innerHTML = `
            <div class="card">
                <header><strong>Resultado</strong></header>
                <pre><code>${formattedJson}</code></pre>
            </div>
        `;
    }

    // função para formatar msg de erro
    function displayError(message) {
        contractsListOutput.innerHTML = ''; // Limpa a lista de contratos, se houver
        resultSection.innerHTML = `<div class="error-message">${message}</div>`;
    }

    // --- Lógica de Login
    loginForm.addEventListener('submit', async (e) => { //async: palavra chave para função que realizará operações demoradas, e: objeto do evento
        e.preventDefault(); //Não recarregar a página
        const loginButton = loginForm.querySelector('button');
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        loginButton.disabled = true; // Desabilita o botão ao clicar 1x
        loginButton.textContent = 'Entrando...';

        // requisição da api
        const formData = new URLSearchParams();   //Formato padrão de resposta que a api espera
        formData.append('username', username);
        formData.append('password', password);

        try {
            // Aqui faz o pedido de login de fato para a api
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }, //formato (etiqueta dos dados)
                body: formData
            });

            if (!response.ok) throw new Error('Usuário ou senha inválidos!'); //Falha caso a api der erro

            const data = await response.json();
            apiToken = data.access_token;   //Aqui pegamos o token da api quando der sucesso de login

            //com o login feito, manipula a página para aparecer a seção de upload
            loginSection.classList.add('hidden');
            appSection.classList.remove('hidden');
            resultSection.innerHTML = '';

        } catch (error) {
            displayError(`Erro no login: ${error.message}`);
        } finally {
            //volta com o default das variáveis
            loginButton.disabled = false;
            loginButton.textContent = 'Entrar';
        }
    });

    // --- Lógica de Upload 
    uploadForm.addEventListener('submit', async (e) => { //async: palavra chave para função que realizará operações demoradas, e: objeto do evento
        e.preventDefault(); //Não recarregar a página
        
        // Verificação token
        if (!apiToken) {
            alert('Token expirado. Relogue');
            return;
        }
        
        const uploadButton = uploadForm.querySelector('button');
        const fileInput = document.getElementById('contract-file');

        // verificação de seleção do arquivo
        if (fileInput.files.length === 0) {
            alert('Por favor, selecione um arquivo para upload.');
            return;
        }
        
        const file = fileInput.files[0]; //como file pode conter vários arquivos, aqui selecionamos o primeiro da lista
        const formData = new FormData(); //criação do objeto (caixa de correio) para a api
        formData.append('file', file); //colocamos o arquivo do upload dentro da "caixa"

        // Feedback visual para o usuário
        uploadButton.disabled = true;
        uploadButton.textContent = 'Analisando...';
        loadingDiv.classList.remove('hidden');
        resultSection.innerHTML = '';
        contractsListOutput.innerHTML = ''; // <-- LIMPA A LISTA TAMBÉM

        try {
            // requisição a api
            const response = await fetch(`${API_URL}/contracts/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${apiToken}` },
                body: formData
            });

            const data = await response.json(); //resposta da api "formatada para js"

            if (!response.ok) {
                // Trata erros
                throw new Error(data.detail || 'Ocorreu um erro no upload.');
            }

            // Mostra o resultado da análise
            displayResult("O Upload foi feito, aguarde alguns segundos para a análise e poderá pesquisar");

        } catch (error) {
            displayError(error.message);
        } finally {
            // Limpa o feedback visual e o arquivo
            uploadButton.disabled = false;
            uploadButton.textContent = 'Analisar';
            loadingDiv.classList.add('hidden');
            fileInput.value = '';
        }
    });

    // --- Lógica de busca 
    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        // Verificação do token
        if (!apiToken) {
            alert('Token expirado. Relogue!');
            return;
        }
        
        const searchButton = searchForm.querySelector('button');
        const filenameInput = document.getElementById('search-filename');
        const filename = filenameInput.value.trim(); //trim para remover espaços

        if (!filename) {
            alert('Por favor, digite um nome de arquivo.');
            return;
        }

        // mudança visual
        searchButton.disabled = true;
        searchButton.textContent = 'Buscando...';
        loadingDiv.classList.remove('hidden');
        resultSection.innerHTML = '';
        contractsListOutput.innerHTML = ''; // <-- LIMPA A LISTA TAMBÉM

        try {
            // requisição a api
            const response = await fetch(`${API_URL}/contracts/${encodeURIComponent(filename)}`, { // Use encodeURIComponent para nomes com caracteres especiais
                method: 'GET',
                headers: { 'Authorization': `Bearer ${apiToken}` }
            });

            const data = await response.json(); //resposta formatada da api

            if (!response.ok) {
                // Se a API retornar um erro
                throw new Error(data.detail || 'Erro ao buscar o contrato.');
            }

            displayResult(data); // Mostra os dados do contrato encontrado

        } catch (error) {
            displayError(error.message);
        } finally {
            //mudança visual default
            searchButton.disabled = false;
            searchButton.textContent = 'Buscar';
            loadingDiv.classList.add('hidden');
        }
    });

    // --- Lógica de Deletar Contrato 
    deleteContractForm.addEventListener('submit', async (e) => { //async: palavra chave para função que realizará operações demoradas, e: objeto do evento
        e.preventDefault(); // Impede o envio padrão do formulário
        
        const deleteButton = deleteContractForm.querySelector('button');
        const filenameToDelete = deleteFilenameInput.value.trim(); // Pega o nome do arquivo e remove espaços extras

        // Verificação de preenchimento do campo
        if (!filenameToDelete) {
            alert('Por favor, insira o nome do arquivo para deletar.');
            return; // Aborta a execução se o campo estiver vazio
        }

        // Verificação do token de autenticação
        if (!apiToken) {
            alert('Token expirado. Relogue!');
            return; // Aborta a execução se o token não existir
        }

        // Feedback visual para o usuário
        deleteButton.disabled = true; // Desabilita o botão
        deleteButton.textContent = 'Deletando...'; // Altera o texto do botão
        loadingDiv.classList.remove('hidden'); // Mostra o indicador de carregamento
        loadingDiv.textContent = 'Deletando contrato...'; // Altera o texto do carregamento
        resultSection.innerHTML = ''; // Limpa a área de resultados de busca/upload
        contractsListOutput.innerHTML = ''; // Limpa a lista de contratos, se houver

        try {
            // Faz uma requisição GET para o endpoint de busca de contrato por nome, que você já possui.
            // O encodeURIComponent é usado para garantir que o nome do arquivo seja seguro para a URL.
            const getContractUrl = `${API_URL}/contracts/${encodeURIComponent(filenameToDelete)}`;
            
            const getResponse = await fetch(getContractUrl, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${apiToken}`, // Inclui o token para autenticação
                    'Content-Type': 'application/json'
                }
            });

            if (!getResponse.ok) {
                // Se a busca falhar 
                const errorData = await getResponse.json(); // Pega a mensagem de erro da API
                if (getResponse.status === 404) {
                    throw new Error(`Contrato com o nome de arquivo "${filenameToDelete}" não encontrado.`);
                } else {
                    // Lança um erro com a mensagem detalhada da API ou uma mensagem genérica
                    throw new Error(errorData.detail || 'Erro ao buscar contrato para deletar.');
                }
            }

            const contractDetails = await getResponse.json(); // Converte a resposta para JSON
            const contractIdToDelete = contractDetails.id; // Extrai o ID do contrato encontrado

            // Passo 2: Usar o ID recuperado para chamar o endpoint de exclusão
            // Agora que temos o ID, fazemos uma requisição DELETE para o endpoint de exclusão por ID.
            const deleteUrl = `${API_URL}/contracts/${contractIdToDelete}`;
            const deleteResponse = await fetch(deleteUrl, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${apiToken}`, // Inclui o token para autenticação
                    'Content-Type': 'application/json'
                }
            });

            const deleteData = await deleteResponse.json(); // Converte a resposta de exclusão para JSON

            if (!deleteResponse.ok) {
                // Se a exclusão falhar
                throw new Error(deleteData.detail || 'Erro ao deletar o contrato.');
            }

            // Exibe mensagem de sucesso na área de resultados
            displayResult({ message: `Contrato "${filenameToDelete}" (ID: ${contractIdToDelete}) deletado com sucesso!` });
            deleteFilenameInput.value = ''; // Limpa o campo de entrada após o sucesso

            // Opcional: Recarregar a lista de contratos se ela estiver visível
            // Se você quiser que a lista de contratos seja atualizada automaticamente após a exclusão:
            // if (!contractsListOutput.classList.contains('hidden')) { // Verifica se a lista está visível
            //     listFilesButton.click(); // Simula o clique no botão de "Ver todos os arquivos" para atualizar a lista
            // }

        } catch (error) {
            // Captura e exibe quaisquer erros que ocorram durante a busca ou a deleção
            displayError(`Erro ao deletar: ${error.message}`);
        } finally {
            // Reseta o feedback visual e o estado do formulário/botão
            deleteButton.disabled = false; // Habilita o botão novamente
            deleteButton.textContent = 'Deletar'; // Restaura o texto original do botão
            loadingDiv.classList.add('hidden'); // Esconde o indicador de carregamento
            loadingDiv.textContent = 'Processando...'; // Reseta o texto do carregamento para o padrão
        }
    });


    // --- Logica de listar os contratos 
    listFilesButton.addEventListener('click', async () => {
        if (!apiToken) {
            alert('Token expirado. Relogue!');
            return;
        }

        // Atualização visual
        loadingDiv.classList.remove('hidden');
        loadingDiv.textContent = 'Buscando lista de arquivos...';
        resultSection.innerHTML = ''; // Limpa a área de resultados de busca/upload
        contractsListOutput.innerHTML = ''; // Limpa a lista antiga

        try {
            // de fato a requisição a api
            const response = await fetch(`${API_URL}/contracts/list/filenames`, {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${apiToken}` }
            });

            const filenames = await response.json(); // resposta da api já formatada

            if (!response.ok) {
                //se a api retornar um erro
                throw new Error(filenames.detail || 'Erro ao buscar a lista de arquivos.');
            }

            if (filenames.length === 0) {
                // se estiver vazio modificar o html
                contractsListOutput.innerHTML = `<p>Nenhum contrato encontrado no banco de dados.</p>`;
            } else {
                // Cria uma lista HTML (<ul>) com os nomes dos arquivos
                const listHtml = filenames.map(name => `<li>${name}</li>`).join('');
                contractsListOutput.innerHTML = `<ul>${listHtml}</ul>`;
            }

        } catch (error) {
            // Em vez de displayError, colocamos o erro na própria área da lista
            contractsListOutput.innerHTML = `<p style="color: red;">${error.message}</p>`;
        } finally {
            loadingDiv.classList.add('hidden');
            loadingDiv.textContent = 'Processando...'; // Reseta o texto do loading
        }
    });
});