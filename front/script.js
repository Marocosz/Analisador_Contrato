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

    const API_URL = 'https://analisador-contratos.onrender.com';  // ATUALIZAAAAA
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
        const formData = new URLSearchParams();  //Formato padrão de resposta que a api espera
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
            apiToken = data.access_token;  //Aqui pegamos o token da api quando der sucesso de login

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
            displayResult(data);

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

    // --- Lógica de busca ---
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
            const response = await fetch(`${API_URL}/contracts/${filename}`, {
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


    // --- Logica de listar os contratos ---
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