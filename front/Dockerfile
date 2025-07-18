# Usamos a imagem oficial e super leve do Nginx.
FROM nginx:1.25-alpine


# Copia todo o conteúdo da pasta 'front' (onde este Dockerfile está)
# para dentro da pasta padrão do Nginx que serve os arquivos na web.
COPY . /usr/share/nginx/html

# Remove a configuração padrão do Nginx que vem com a imagem.
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nosso próprio arquivo de configuração para o Nginx.
COPY nginx.conf /etc/nginx/conf.d/