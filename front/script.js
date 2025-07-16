document.addEventListener('DOMContentLoaded', () => {
    const loginSection = document.getElementById('login-section');
    const uploadSection = document.getElementById('upload-section');
    const loginForm = document.getElementById('login-form');
    const uploadForm = document.getElementById('upload-form');
    const resultSection = document.getElementById('result-section');
    const loadingDiv = document.getElementById('loading');

    const API_URL = 'http://127.0.0.1:8000'; // URL da sua API FastAPI
    let apiToken = null;

    // --- Lógica de Login ---
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            if (!response.ok) throw new Error('Usuário ou senha inválidos!');
            
            const data = await response.json();
            apiToken = data.access_token;

            // Esconde o login e mostra o upload
            loginSection.classList.add('hidden');
            uploadSection.classList.remove('hidden');
            resultSection.innerHTML = '<p style="color: green;">Login realizado com sucesso!</p>';

        } catch (error) {
            resultSection.innerHTML = `<div class="error-message">Erro no login: ${error.message}</div>`;
        }
    });

    // --- Lógica de Upload ---
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const fileInput = document.getElementById('contract-file');
        if (fileInput.files.length === 0) {
            alert('Por favor, selecione um arquivo.');
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        loadingDiv.classList.remove('hidden');
        resultSection.innerHTML = '';

        try {
            const response = await fetch(`${API_URL}/contracts/upload`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${apiToken}` },
                body: formData
            });

            const data = await response.json();

            if (!response.ok) throw new Error(data.detail || 'Ocorreu um erro no servidor.');
            
            // Exibe os resultados formatados
            resultSection.innerHTML = `
                <h3>Análise Concluída!</h3>
                <pre>${JSON.stringify(data, null, 2)}</pre>
            `;

        } catch (error) {
            resultSection.innerHTML = `<div class="error-message">Erro no upload: ${error.message}</div>`;
        } finally {
            loadingDiv.classList.add('hidden');
        }
    });
});