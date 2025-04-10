#Define a imagem base
FROM python:3.9

#Define o dirtório de trabalho dentro do controller
WORKDIR /app

#Copia os arquivos de requisistos para o diretório de trabahlo
COPY requirements.txt .

#Copia os arquivos de requisitos para o diretório de trabalho
RUN pip install --no-cache-dir -r requirements.txt

#Copia o código-fonte para o diretório de trabalho
COPY . .

EXPOSE 5003

#Define o comande de execução da API
CMD ["flask", "run", "--host","0.0.0.0", "--port=5003"]